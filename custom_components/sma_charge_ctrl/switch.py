"""sma charge ctrl sensor platform."""
# s. /workspaces/ha-core/homeassistant/components/demo/switch.py
import logging

from pymodbus.client import ModbusTcpClient

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_UNIT_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the demo switch platform."""

    mdb_cl = hass.data[DOMAIN].get(config_entry.entry_id)
    unit_id = config_entry[CONF_UNIT_ID]  # noqa: F841

    if not mdb_cl:
        return False

    async_add_entities(
        [
            SmaChargingSwitch("SMA Charge Switch", mdb_cl),
        ]
    )


# s. /workspaces/ha-core/homeassistant/components/demo/switch.py
class SmaChargingSwitch(SwitchEntity):
    """Class to switch on/off charging."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(self, name, pymodbus_client: ModbusTcpClient) -> None:  # noqa: D107
        self._name = name
        self._pymodbus_client = pymodbus_client

        self._attr_name = name
        self._attr_is_on = False
        self._attr_device_class = SwitchDeviceClass.SWITCH
        self._attr_unique_id = name + "_" + str(pymodbus_client)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=name,
        )

    # @property
    # def name(self):  # noqa: D102
    #     return self._name

    @property
    def is_on(self):  # noqa: D102
        return bool(self._attr_is_on)

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self._attr_is_on = True
        self.schedule_update_ha_state()
        _LOGGER.debug("Charging turned ON")

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._attr_is_on = False
        self.schedule_update_ha_state()
        _LOGGER.debug("Charging turned OFF")
