"""sma charge ctrl sensor platform."""
# s. /workspaces/ha-core/homeassistant/components/demo/switch.py
import logging

from pymodbus.client import ModbusTcpClient

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api.api import Api
from .api.modbus_host import ModbusHostHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the demo switch platform."""
    _LOGGER.debug("switch.async_setup_entry")
    hub: ModbusHostHub = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            SmaChargingSwitch("Charge from Net", hub.mdb_cl, hub.unit_id),
            SmaDischargingSwitch("Discharge Battery", hub.mdb_cl, hub.unit_id),
        ]
    )


class SmaSwitchBase(SwitchEntity):
    """Base class."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(self, name, pymodbus_client: ModbusTcpClient, unit_id: int) -> None:  # noqa: D107
        self._name = name
        self._pymodbus_client = pymodbus_client
        self._unit_id = unit_id

        self._attr_name = name
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

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._attr_is_on = False
        self.schedule_update_ha_state()


class SmaChargingSwitch(SmaSwitchBase):
    """Class to switch on/off charging."""

    _attr_is_on = False

    # @property
    # def name(self):  # noqa: D102
    #     return self._name

    @property
    def is_on(self):  # noqa: D102
        return bool(self._attr_is_on)

    def turn_on(self, **kwargs):
        """Turn the device on."""
        super().turn_on()
        _LOGGER.debug("Charging turned ON")
        self.start_charging_from_net()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        super().turn_off()
        _LOGGER.debug("Charging turned OFF")
        self.stop_charging_from_net()

    def start_charging_from_net(self):
        """Ladevorgang der Batterie vom Netz starten."""

        return Api.battery_start_charging_from_net(self._pymodbus_client, self._unit_id)

    def stop_charging_from_net(self):
        """Ladevorgang beenden, Entladevorgang der Batterie erlauben."""
        return Api.battery_stop_charging_from_net(
            self._pymodbus_client, self._unit_id, discharge_power=0
        )


class SmaDischargingSwitch(SmaSwitchBase):
    """Class to switch on/off charging."""

    _attr_is_on = True

    # @property
    # def name(self):  # noqa: D102
    #     return self._name

    @property
    def is_on(self):  # noqa: D102
        return bool(self._attr_is_on)

    def turn_on(self, **kwargs):
        """Turn the device on."""
        super().turn_on()
        _LOGGER.debug("Discharging turned ON")
        self.start_discharging()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        super().turn_off()
        _LOGGER.debug("Discharging turned OFF")
        self.stop_discharging()

    def start_discharging(self):
        """Entladevorgang der Batterie verbieten."""
        client = self._pymodbus_client
        unit_id = self._unit_id
        return Api.battery_start_discharging(client, unit_id, discharge_power=0)

    def stop_discharging(self):
        """Entladevorgang der Batterie verbieten."""
        return self.set_battery_discharge_power(0)
