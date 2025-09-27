import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data.get("wallbox_coordinator")  # kann None sein
    client = data["client"]

    # Bevorzugt das Wallbox-Device; wenn (noch) nicht vorhanden, ans Smartmeter hängen
    device_info = data.get("wallbox_device_info") or data.get("device_info")

    if not coordinator:
        _LOGGER.info(
            "Kein Wallbox-Coordinator vorhanden – BatteryUsageSwitch wird übersprungen."
        )
        return

    entity = BatteryUsageSwitch(coordinator, client, device_info, entry.entry_id)
    async_add_entities([entity], update_before_add=False)


class BatteryUsageSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, client, device_info: DeviceInfo, entry_id: str):
        super().__init__(coordinator)
        self._client = client
        self._attr_name = "Battery Usage bei PV"
        # pro Config-Eintrag eindeutig, falls Integration mehrfach vorhanden ist
        self._attr_unique_id = f"{entry_id}_ksem_battery_usage"
        self._attr_device_info = device_info

    @property
    def available(self) -> bool:
        # verfügbar, wenn Coordinator zuletzt erfolgreich und energyflow_config vorhanden ist
        if not self.coordinator.last_update_success:
            return False
        data = self.coordinator.data or {}
        return "energyflow_config" in data

    @property
    def is_on(self):
        cfg = (self.coordinator.data or {}).get("energyflow_config") or {}
        return bool(cfg.get("batteryusage", False))

    async def async_turn_on(self, **kwargs):
        await self._client.set_battery_usage(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self._client.set_battery_usage(False)
        await self.coordinator.async_request_refresh()
