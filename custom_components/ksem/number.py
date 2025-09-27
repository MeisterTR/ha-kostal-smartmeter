import logging
from homeassistant.components.number import NumberEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN
from .helper import first_evse_from_coordinator  # <— Single-WB Helfer

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    client = data["client"]
    wallbox_coord = data.get("wallbox_coordinator")
    device_info_from_sensor = data.get("wallbox_device_info")
    last_ws_data = data.get("last_chargemode", {}) or {}

    from .helper import (
        first_evse_from_coordinator,
    )  # sicherstellen, dass der Import stimmt

    entities_created = False  # <- NEU: verhindert doppelte Anlage

    def _build_wb_device_info(wb: dict) -> DeviceInfo:
        uuid = wb.get("uuid")
        label = wb.get("label", "Wallbox")
        model = wb.get("model", "")
        details = wb.get("details") or {}
        serial = details.get("serial", uuid)
        version = details.get("version", "")
        return DeviceInfo(
            identifiers={(DOMAIN, f"wallbox-{uuid}")},
            name=f"Wallbox {label}",
            model=model,
            serial_number=serial,
            sw_version=version,
            manufacturer="Kostal",
        )

    async def _create_entities_if_possible():
        nonlocal entities_created
        if entities_created:
            return  # schon erzeugt
        wb = first_evse_from_coordinator(wallbox_coord)
        if not wb:
            return  # (noch) keine WB sichtbar

        wb_device_info = device_info_from_sensor or _build_wb_device_info(wb)

        entity1 = MinPvPowerQuota(
            client=client,
            device_info=wb_device_info,
            initial=last_ws_data.get("minpvpowerquota", 0),
            entry_id=entry.entry_id,
            wallbox_coord=wallbox_coord,
        )
        entity2 = MinChargingPowerQuota(
            client=client,
            device_info=wb_device_info,
            initial=last_ws_data.get("mincharginpowerquota", 0),
            entry_id=entry.entry_id,
            wallbox_coord=wallbox_coord,
        )

        async_add_entities([entity1, entity2])
        hass.data[DOMAIN][entry.entry_id]["quota_entities"] = {
            "minpv": entity1,
            "mincharge": entity2,
        }
        entities_created = True  # <- markiert als fertig

    # 1) Sofort versuchen
    await _create_entities_if_possible()

    # 2) Später nachziehen, aber ohne doppelt zu feuern
    if wallbox_coord and not entities_created:

        def _wb_listener():
            hass.async_create_task(_create_entities_if_possible())

        wallbox_coord.async_add_listener(_wb_listener)


class _WBAvailableMixin:
    """Macht Entities automatisch 'unavailable', wenn die (eine) Wallbox offline ist."""

    def __init__(self, wallbox_coord):
        self._wallbox_coord = wallbox_coord

    @property
    def available(self) -> bool:
        if not self._wallbox_coord or not self._wallbox_coord.last_update_success:
            return False
        wb = first_evse_from_coordinator(self._wallbox_coord)
        return bool(wb and wb.get("available", True))


class MinPvPowerQuota(_WBAvailableMixin, NumberEntity):
    def __init__(
        self, client, device_info: DeviceInfo, initial, entry_id, wallbox_coord
    ):
        _WBAvailableMixin.__init__(self, wallbox_coord)
        self._entry_id = entry_id
        self._client = client
        self._attr_name = "Min PV Power"
        self._attr_unique_id = f"{entry_id}_ksem_minpvpowerquota"
        self._attr_device_info = device_info
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 10
        self._value = int(initial or 0)

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float):
        await self._client.set_charge_mode(
            mode=None,
            minpvpowerquota=int(value),
            mincharginpowerquota=None,
            entry_id=self._entry_id,
        )
        self._value = int(value)
        self.async_write_ha_state()

    def update_value(self, value: int):
        self._value = int(value)
        self.async_write_ha_state()


class MinChargingPowerQuota(_WBAvailableMixin, NumberEntity):
    def __init__(
        self, client, device_info: DeviceInfo, initial, entry_id, wallbox_coord
    ):
        _WBAvailableMixin.__init__(self, wallbox_coord)
        self._entry_id = entry_id
        self._client = client
        self._attr_name = "Min Charging Power"
        self._attr_unique_id = f"{entry_id}_ksem_mincharginpowerquota"
        self._attr_device_info = device_info
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 25
        self._value = int(initial or 0)

    @property
    def native_value(self):
        return self._value

    async def async_set_native_value(self, value: float):
        await self._client.set_charge_mode(
            mode=None,
            mincharginpowerquota=int(value),
            minpvpowerquota=None,
            entry_id=self._entry_id,
        )
        self._value = int(value)
        self.async_write_ha_state()

    def update_value(self, value: int):
        self._value = int(value)
        self.async_write_ha_state()
