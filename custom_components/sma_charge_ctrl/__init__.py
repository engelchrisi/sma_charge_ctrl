"""SMA Chart Ctrl Custom Component."""
import logging

from pymodbus.client import ModbusTcpClient

from homeassistant import config_entries, core
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, Platform

from .api.api import Api
from .api.modbus_host import ModbusHostHub
from .const import CONF_UNIT_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]  # , Platform.SWITCH]


def _setup_services(hass: core.HomeAssistant, client: ModbusTcpClient, unit_id: int):
    """Set up is called when Home Assistant is loading our component."""
    _LOGGER.debug("__init__._setup_services")

    Api.get_default_values(client, unit_id)

    def _battery_start_charging_from_net(call: core.ServiceCall) -> None:
        """Handle the service call."""
        charge_power = call.data.get("charge_power", -1)
        Api.battery_start_charging_from_net(client, unit_id, charge_power)

    hass.services.async_register(
        DOMAIN, "battery_start_charging_from_net", _battery_start_charging_from_net
    )

    def _battery_start_charging_from_pv(call: core.ServiceCall) -> None:
        """Start the battery loading from PV + discharging."""
        Api.battery_start_charging_from_pv(client, unit_id)

    hass.services.async_register(
        DOMAIN, "battery_start_charging_from_pv", _battery_start_charging_from_pv
    )

    def _battery_stop_charging_from_net(call: core.ServiceCall) -> None:
        """Handle the service call."""
        discharge_power = call.data.get("discharge_power", 0)
        Api.battery_stop_charging_from_net(client, unit_id, discharge_power)

    hass.services.async_register(
        DOMAIN, "battery_stop_charging_from_net", _battery_stop_charging_from_net
    )

    def _battery_start_discharging(call: core.ServiceCall) -> None:
        """Handle the service call."""
        discharge_power = call.data.get("discharge_power", 1500)
        Api.battery_start_discharging(client, unit_id, discharge_power)

    hass.services.async_register(
        DOMAIN, "battery_start_discharging", _battery_start_discharging
    )

    def _battery_stop_discharging(call: core.ServiceCall) -> None:
        """Stop the battery from discharging its energy."""
        Api.battery_stop_discharging(client, unit_id)

    hass.services.async_register(
        DOMAIN, "battery_stop_discharging", _battery_stop_discharging
    )

    # Return boolean to indicate that initialization was successful.
    return True


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up platform from a ConfigEntry."""
    hass.data.setdefault(DOMAIN, {})
    hass_data = dict(entry.data)
    _LOGGER.debug("__init__.async_setup_entry")

    hostname = hass_data[CONF_HOST]

    mdb_host = ModbusHostHub(
        name=hass_data[CONF_NAME],
        host=hostname,
        port=int(hass_data[CONF_PORT]),
        unit_id=int(hass_data[CONF_UNIT_ID]),
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = mdb_host

    _setup_services(hass, mdb_host.mdb_cl, mdb_host.unit_id)

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Remove config entry from domain.
        # entry_data = hass.data[DOMAIN].pop(entry.entry_id)
        # Remove options_update_listener.
        # entry_data["unsub_options_update_listener"]()
        pass

    return unload_ok


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the GitHub Custom component from yaml configuration."""
    hass.data.setdefault(DOMAIN, {})
    return True
