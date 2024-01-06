# s. https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_1/
"""SMA Chart Ctrl Custom Component."""
import logging

import voluptuous as vol

from homeassistant.const import SERVICE_RELOAD
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.reload import async_reload_integration_platforms
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS, STARTUP_MESSAGE




# async def async_setup_entry(
#     hass: core.HomeAssistant, entry: config_entries.ConfigEntry
# ) -> bool:
#     """Set up platform from a ConfigEntry."""
#     hass.data.setdefault(DOMAIN, {})
#     hass.data[DOMAIN][entry.entry_id] = entry.data

#     # Forward the setup to the sensor platform.
#     hass.async_create_task(
#         hass.config_entries.async_forward_entry_setup(entry, "sensor")
#     )
#     return True

_LOGGER = logging.getLogger(__name__)

# s. https://github.com/Limych/ha-average/blob/dev/custom_components/average/__init__.py
async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the platforms."""
    # Print startup message
    _LOGGER.info(STARTUP_MESSAGE)

    # await async_setup_reload_service(hass, DOMAIN, PLATFORMS)

    component = EntityComponent(_LOGGER, DOMAIN, hass)  # noqa: F841

    async def reload_service_handler(service: ServiceCall) -> None:
        """Reload all average sensors from config."""
        # print("+++++++++++++++++++++++++")
        # print(component)
        # print(hass.data[DATA_INSTANCES]["sensor"].entities[0])

        await async_reload_integration_platforms(hass, DOMAIN, PLATFORMS)

    hass.services.async_register(
        DOMAIN, SERVICE_RELOAD, reload_service_handler, schema=vol.Schema({})
    )

    return True
