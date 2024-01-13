"""SMA Chart Ctrl Custom Component."""
import logging

from homeassistant import config_entries, core
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, Platform

from .const import CONF_UNIT_ID, DOMAIN
from .modbus_host import ModbusHostHub

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]


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
