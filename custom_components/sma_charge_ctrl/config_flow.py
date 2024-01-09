"""bla."""
import logging
from typing import Any, Optional

import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
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

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):  # noqa: D102
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_auth(user_input[CONF_HOST], self.hass)
            except ValueError:
                errors["base"] = "auth"
            if not errors:
                # Input is valid, set data.
                self.data = user_input

                # User is done adding repos, create the config entry.
                return self.async_create_entry(title="SMA Bla", data=self.data)

        return self.async_show_form(
            step_id="user", data_schema=MAIN_SCHEMA, errors=errors
        )

    # async def async_step_repo(self, user_input: Optional[dict[str, Any]] = None):
    #     """Second step in config flow to add a repo to watch."""
    #     errors: dict[str, str] = {}
    #     if user_input is not None:
    #         # Validate the path.
    #         try:
    #             await validate_path(
    #                 user_input[CONF_PATH], self.data[CONF_ACCESS_TOKEN], self.hass
    #             )
    #         except ValueError:
    #             errors["base"] = "invalid_path"

    #         if not errors:
    #             # Input is valid, set data.
    #             self.data[self.CONF_REPOS].append(
    #                 {
    #                     "path": user_input[CONF_PATH],
    #                     "name": user_input.get(CONF_NAME, user_input[CONF_PATH]),
    #                 }
    #             )
    #             # If user ticked the box show this form again so they can add an
    #             # additional repo.
    #             if user_input.get("add_another", False):
    #                 return await self.async_step_repo()

    #             # User is done adding repos, create the config entry.
    #             return self.async_create_entry(title="GitHub Custom", data=self.data)

    #     return self.async_show_form(
    #         step_id="repo", data_schema=REPO_SCHEMA, errors=errors
    #     )

    # @staticmethod
    # @callback
    # def async_get_options_flow(config_entry):
    #     """Get the options flow for this handler."""
    #     return OptionsFlowHandler(config_entry)


# class OptionsFlowHandler(config_entries.OptionsFlow):
#     """Handles options flow for the component."""

#     def __init__(self, config_entry: config_entries.ConfigEntry) -> None:  # noqa: D107
#         self.config_entry = config_entry

#     async def async_step_init(
#         self, user_input: dict[str, Any] = None
#     ) -> dict[str, Any]:
#         """Manage the options for the custom component."""
#         errors: dict[str, str] = {}
#         # Grab all configured repos from the entity registry so we can populate the
#         # multi-select dropdown that will allow a user to remove a repo.
#         entity_registry = async_get(self.hass)
#         entries = async_entries_for_config_entry(
#             entity_registry, self.config_entry.entry_id
#         )
#         # Default value for our multi-select.
#         all_repos = {e.entity_id: e.original_name for e in entries}

#         if user_input is not None:
#             if user_input.get(CONF_PATH):
#                 # Validate the path.
#                 access_token = self.hass.data[DOMAIN][self.config_entry.entry_id][
#                     CONF_ACCESS_TOKEN
#                 ]
#                 try:
#                     await validate_path(user_input[CONF_PATH], access_token, self.hass)
#                 except ValueError:
#                     errors["base"] = "invalid_path"

#             if not errors:
#                 # Value of data will be set on the options property of our config_entry
#                 # instance.
#                 return self.async_create_entry(
#                     title="",
#                     data={self.CONF_REPOS: None},
#                 )

#         options_schema = vol.Schema(
#             {
#                 vol.Optional("repos", default=list(all_repos.keys())): cv.multi_select(
#                     all_repos
#                 ),
#                 vol.Optional(CONF_PATH): cv.string,
#                 vol.Optional(CONF_NAME): cv.string,
#             }
#         )
#         return self.async_show_form(
#             step_id="init", data_schema=options_schema, errors=errors
#         )
