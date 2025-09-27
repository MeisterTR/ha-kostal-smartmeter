import asyncio
import json
import logging
from typing import Optional

from aiohttp import WSMsgType
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .helper import first_evse_from_coordinator  # Single-WB Helfer

_LOGGER = logging.getLogger(__name__)

MODE_MAP = {
    "lock": "Lock Mode",
    "grid": "Power Mode",
    "pv": "Solar Pure Mode",
    "hybrid": "Solar Plus Mode",
}
REVERSE_MODE_MAP = {v: k for k, v in MODE_MAP.items()}

PHASE_MAP = {0: "3 Phasen", 1: "1 Phase", 2: "Automatisch"}
REVERSE_PHASE_MAP = {v: k for k, v in PHASE_MAP.items()}


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    coordinator = data.get("wallbox_coordinator")  # kann None sein

    entities = []

    # --- Nur anlegen, wenn eine Wallbox erkennbar ist (läuft aber auch ohne WB) ---
    wb = first_evse_from_coordinator(coordinator) if coordinator else None
    if wb:
        entities.append(
            KsemChargeModeSelect(
                hass=hass,
                entry_id=entry.entry_id,
                client=client,
                token=None,  # Token wird im WS-Loop frisch geholt
                coordinator=coordinator,
            )
        )
        entities.append(
            KsemPhaseSwitchSelect(
                hass=hass,
                entry_id=entry.entry_id,
                coordinator=coordinator,
                client=client,
            )
        )

    if entities:
        async_add_entities(entities, update_before_add=False)

    # --- Später automatisch nachziehen, falls beim Start noch keine WB vorhanden war ---
    if coordinator and not wb:

        async def _maybe_add_single_wb():
            wb_now = first_evse_from_coordinator(coordinator)
            if not wb_now:
                return
            new_entities = [
                KsemChargeModeSelect(
                    hass=hass,
                    entry_id=entry.entry_id,
                    client=client,
                    token=None,
                    coordinator=coordinator,
                ),
                KsemPhaseSwitchSelect(
                    hass=hass,
                    entry_id=entry.entry_id,
                    coordinator=coordinator,
                    client=client,
                ),
            ]
            async_add_entities(new_entities, update_before_add=False)

        def _wb_listener():
            hass.async_create_task(_maybe_add_single_wb())

        coordinator.async_add_listener(_wb_listener)
        await _maybe_add_single_wb()


class KsemPhaseSwitchSelect(CoordinatorEntity, SelectEntity):
    """Phasenumschaltung (nur eine WB)."""

    def __init__(self, hass, entry_id, coordinator, client):
        super().__init__(coordinator)
        self._hass = hass
        self._entry_id = entry_id
        self._client = client
        self._attr_name = "Phasenumschaltung"
        self._attr_unique_id = f"{entry_id}_ksem_phase_switch"
        self._attr_options = list(PHASE_MAP.values())

    # DeviceInfo dynamisch: wenn WB existiert -> Wallbox, sonst Smartmeter
    @property
    def device_info(self):
        data = self._hass.data[DOMAIN][self._entry_id]
        return data.get("wallbox_device_info") or data.get("device_info")

    @property
    def available(self) -> bool:
        if not self.coordinator.last_update_success:
            return False
        return first_evse_from_coordinator(self.coordinator) is not None

    @property
    def current_option(self) -> Optional[str]:
        data = self.coordinator.data or {}
        val = data.get("phase_usage_state", 0)
        return PHASE_MAP.get(val)

    async def async_select_option(self, option: str):
        if option not in REVERSE_PHASE_MAP:
            _LOGGER.warning("Ungültige Auswahl: %s", option)
            return
        new_value = REVERSE_PHASE_MAP[option]
        await self._client.set_phase_switching(new_value)
        await self.coordinator.async_request_refresh()


class KsemChargeModeSelect(SelectEntity):
    """Lademodus-Auswahl per WebSocket-Backfeed (nur eine WB)."""

    def __init__(self, hass, entry_id, client, token, coordinator):
        self._hass = hass
        self._entry_id = entry_id
        self._client = client
        self._token = token  # optional; im Loop jeweils frisch geholt
        self._coord = coordinator  # für available()
        self._attr_name = "Wallbox Charge Mode"
        self._attr_unique_id = f"{entry_id}_ksem_charge_mode"
        self._attr_options = list(MODE_MAP.values())
        self._api_mode: Optional[str] = None
        self._ws_task: Optional[asyncio.Task] = None

    # DeviceInfo dynamisch: wenn WB existiert -> Wallbox, sonst Smartmeter
    @property
    def device_info(self):
        data = self._hass.data[DOMAIN][self._entry_id]
        return data.get("wallbox_device_info") or data.get("device_info")

    @property
    def available(self) -> bool:
        if not self._coord or not self._coord.last_update_success:
            return False
        return first_evse_from_coordinator(self._coord) is not None

    @property
    def current_option(self) -> Optional[str]:
        return MODE_MAP.get(self._api_mode)

    async def async_select_option(self, option: str):
        mode = REVERSE_MODE_MAP.get(option)
        if mode:
            await self._client.set_charge_mode(
                mode=mode,
                minpvpowerquota=None,
                mincharginpowerquota=None,
                entry_id=self._entry_id,
            )
            self._api_mode = mode
            self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        if not self._ws_task:
            self._ws_task = self._hass.loop.create_task(self._listen_websocket())

    async def async_will_remove_from_hass(self) -> None:
        if self._ws_task and not self._ws_task.done():
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
        self._ws_task = None

    async def _listen_websocket(self):
        url = f"ws://{self._client.host}/api/data-transfer/ws/json/json/local/config/e-mobility/chargemode"
        session = async_get_clientsession(self._hass)

        while True:
            token = self._token or getattr(
                getattr(self._client, "token", None), "access_token", None
            )
            if not token:
                _LOGGER.warning(
                    "Kein Token für WebSocket verfügbar – neuer Versuch in 30s."
                )
                await asyncio.sleep(30)
                continue

            try:
                async with session.ws_connect(
                    url, headers={"Authorization": f"Bearer {token}"}
                ) as ws:
                    await ws.send_str(f"Bearer {token}")
                    _LOGGER.info("WebSocket verbunden für Lademodus")

                    async for msg in ws:
                        if msg.type == WSMsgType.TEXT:
                            try:
                                data = json.loads(msg.data)
                            except Exception as e:
                                _LOGGER.warning("WebSocket JSON decode error: %s", e)
                                continue

                            if not isinstance(data, dict):
                                continue
                            if not (data.get("topic", "") or "").endswith("chargemode"):
                                continue

                            msg_data = data.get("msg", {}) or {}
                            mode = msg_data.get("mode")
                            if mode and mode != self._api_mode:
                                _LOGGER.debug("WebSocket Update: mode=%s", mode)
                                self._api_mode = mode
                                self.async_write_ha_state()

                            # Quoten live an Numbers weiterreichen (falls vorhanden)
                            quotas = self._hass.data[DOMAIN][self._entry_id].get(
                                "quota_entities", {}
                            )
                            if "minpv" in quotas and "minpvpowerquota" in msg_data:
                                quotas["minpv"].update_value(
                                    msg_data["minpvpowerquota"]
                                )
                            if (
                                "mincharge" in quotas
                                and "mincharginpowerquota" in msg_data
                            ):
                                quotas["mincharge"].update_value(
                                    msg_data["mincharginpowerquota"]
                                )

                            # Letzten Stand zwischenspeichern
                            self._hass.data[DOMAIN][self._entry_id][
                                "last_chargemode"
                            ] = msg_data

                        elif msg.type == WSMsgType.ERROR:
                            _LOGGER.warning("WebSocket-Fehler: %s", msg)
                            break

            except asyncio.CancelledError:
                _LOGGER.debug("WebSocket-Task wurde abgebrochen.")
                break
            except Exception as err:
                _LOGGER.error("WebSocket-Verbindung fehlgeschlagen: %s", err)

            _LOGGER.info("WebSocket getrennt, versuche Neuverbindung in 30 Sekunden...")
            await asyncio.sleep(30)
