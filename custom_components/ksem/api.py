import logging
import datetime
from typing import Union
from aiohttp import ClientResponse
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .helper import bearer_header
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class Tokens:
    """Hält Access-Token und Ablaufdatum"""

    def __init__(self, access_token: str, token_type: str, expires_in: int):
        self.access_token = access_token
        self.expire_date = datetime.datetime.now() + datetime.timedelta(
            seconds=expires_in
        )
        _LOGGER.debug("Token erstellt, gültig bis %s", self.expire_date)


class InvalidAuth(Exception):
    """Fehlerhafte Authentifizierung"""


class KsemClient:
    """Client für REST-Aufrufe an die KSEM API mit Token-Refresh"""

    def __init__(self, hass, host: str, password: str) -> None:
        self.hass = hass
        self.host = host.rstrip("/")
        self.password = password
        self.token: Tokens | None = None
        _LOGGER.debug("KsemClient initialisiert für Host %s", self.host)

    async def _auth(self, session):
        url = f"http://{self.host}/api/web-login/token"
        data = {
            "grant_type": "password",
            "client_id": "emos",
            "client_secret": "56951025",
            "username": "admin",
            "password": self.password,
        }
        _LOGGER.debug("Auth POST %s", url)
        resp = await session.post(url, data=data)
        resp.raise_for_status()
        token_data = await resp.json()
        if "error" in token_data:
            raise InvalidAuth("Unauthorized")
        self.token = Tokens(
            token_data["access_token"],
            token_data.get("token_type", ""),
            token_data.get("expires_in", 0),
        )

    async def _put(
        self, path: str, data=None, json=None, headers=None, text_mode=False
    ) -> Union[dict, None]:
        session = async_get_clientsession(self.hass)
        if not self.token or datetime.datetime.now() > self.token.expire_date:
            await self._auth(session)
        url = f"http://{self.host}{path}"
        default_headers = bearer_header(self.token.access_token)
        if headers:
            default_headers.update(headers)

        _LOGGER.debug("PUT %s - Data: %s", url, json or data)
        resp = await session.put(url, headers=default_headers, data=data, json=json)
        if resp.status in (401, 500):
            _LOGGER.debug("Status %s, re-authenticating", resp.status)
            await self._auth(session)
            default_headers = bearer_header(self.token.access_token)
            resp = await session.put(url, headers=default_headers, data=data, json=json)

        if resp.status == 204:
            return None
        resp.raise_for_status()
        return await (resp.text() if text_mode else resp.json())

    async def _get(self, path: str) -> Union[dict, list]:
        session = async_get_clientsession(self.hass)
        if not self.token or datetime.datetime.now() > self.token.expire_date:
            await self._auth(session)
        url = f"http://{self.host}{path}"
        headers = bearer_header(self.token.access_token)
        _LOGGER.debug("GET %s", url)
        resp: ClientResponse = await session.get(url, headers=headers)
        if resp.status in (401, 500):
            _LOGGER.debug("Status %s, re-authenticating", resp.status)
            await self._auth(session)
            headers = bearer_header(self.token.access_token)
            resp = await session.get(url, headers=headers)
        resp.raise_for_status()
        data = await resp.json()
        _LOGGER.debug("Daten erhalten: %s", data)
        return data

    async def get_device_status(self) -> dict:
        _LOGGER.info("Hole Gerätestatus")
        return await self._get("/api/device-settings/deviceusage")

    async def get_device_info(self) -> dict:
        _LOGGER.info("Hole Geräteinformationen")
        return await self._get("/api/device-settings")

    async def get_evse_list(self):
        """Liefert die Liste aller Wallboxen (EVSE) mit UUID etc."""
        _LOGGER.info("Hole Wallboxen-Liste")
        return await self._get("/api/e-mobility/evselist")

    async def get_evse_details(self, evse_id):
        """Liefert Geräte-Details einer Wallbox."""
        _LOGGER.info("Hole Wallbox-Details für ID %s", evse_id)
        return await self._get("/api/evse-kostal/evse/" + evse_id + "/details")

    async def get_evse_state(self):
        """Liefert den aktuellen Status (z. B. charging) einer Wallbox."""
        _LOGGER.info("Hole Wallbox-Status")
        return await self._get("/api/e-mobility/state")

    async def set_charge_mode(
        self,
        mode: str | None = None,
        mincharginpowerquota: int | None = None,
        minpvpowerquota: int | None = None,
        entry_id=None,
    ):
        session = async_get_clientsession(self.hass)
        await self._auth(session)
        url = f"http://{self.host}/api/e-mobility/config/chargemode"

        # Hole aktuelle Werte aus dem WebSocket-Cache
        cache = (
            self.hass.data.get("ksem", {}).get(entry_id, {}).get("last_chargemode", {})
        )

        payload = {
            "mode": mode or cache.get("mode", "lock"),
            "mincharginpowerquota": mincharginpowerquota
            if mincharginpowerquota is not None
            else cache.get("mincharginpowerquota", 100),
            "minpvpowerquota": minpvpowerquota
            if minpvpowerquota is not None
            else cache.get("minpvpowerquota", 30),
        }

        # Füge automatisch die letzten Werte und controlledby=0 hinzu
        payload["lastminchargingpowerquota"] = payload["mincharginpowerquota"]
        payload["lastminpvpowerquota"] = payload["minpvpowerquota"]
        payload["controlledby"] = 0

        headers = bearer_header(self.token.access_token)
        _LOGGER.debug("PUT %s - Payload: %s", url, payload)
        resp = await session.put(url, headers=headers, json=payload)
        resp.raise_for_status()

    async def get_phase_switching(self):
        return await self._get("/api/e-mobility/config/phaseswitching")

    async def set_phase_switching(self, phase_usage: int):
        # KSEM antwortet hier oft ohne JSON/Content-Type
        return await self._put(
            "/api/e-mobility/config/phaseswitching",
            json={"phase_usage": phase_usage},
            text_mode=True,  # <— wichtig
        )

    async def get_energyflow_config(self):
        _LOGGER.info("Hole Configdaten von Energiefluss")
        return await self._get("/api/kostal-energyflow/configuration")

    async def set_battery_usage(self, enabled: bool):
        value = "true" if enabled else "false"
        await self._put(
            "/api/kostal-energyflow/configuration/batteryusage",
            data=value,
            headers={"Content-Type": "text/plain"},
            text_mode=True,
        )
