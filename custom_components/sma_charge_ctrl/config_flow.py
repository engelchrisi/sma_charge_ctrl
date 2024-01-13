"""bla."""
import logging
from typing import Any, Optional

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_UNIT_ID, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

MAIN_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST, default="192.168.178.56"): cv.string,
        vol.Required(CONF_PORT, default=502): cv.port,
        vol.Required(CONF_UNIT_ID, default=3): cv.positive_int,
    }
)


OPTIONS_SHCEMA = vol.Schema({vol.Optional(CONF_NAME, default="foo"): cv.string})


async def validate_path(path: str, access_token: str, hass: core.HomeAssistant) -> None:  # noqa: D103
    pass


async def validate_auth(access_token: str, hass: core.HomeAssistant) -> None:  # noqa: D103
    pass


class SmaChargeCtrlCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """SMA Charge Ctrl Custom config flow."""

    data: Optional[dict[str, Any]]

    async def async_step_user(
        self, user_input: Optional[dict[str, Any]] = None
    ) -> FlowResult:
        """UI step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_auth(user_input[CONF_HOST], self.hass)
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data = user_input

                # self._abort_if_unique_id_configured(updates={CONF_HOST: device.host})

                # User is done adding repos, create the config entry.
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=self.data
                )

        return self.async_show_form(
            step_id="user", data_schema=MAIN_SCHEMA, errors=errors
        )
