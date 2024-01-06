"""SMA Charge Ctrl."""
from datetime import timedelta
from typing import Final

# Base component constants
from homeassistant.const import Platform

NAME: Final = "SMA Charge Ctrl"
DOMAIN: Final = "sma_charge_ctrl"
VERSION: Final = "0.1.0"
DEPOT_URL: Final = "https://github.com/engelchrisi/sma_charge_ctrl"


STARTUP_MESSAGE: Final = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
Clone this depot to adapt your own SMA device:
{DEPOT_URL}
-------------------------------------------------------------------
"""

PLATFORMS = [
    Platform.SENSOR,
]

# Defaults
DEFAULT_NAME: Final = "SmaChargeController"

# Attributes
ATTR_HOST_PORT: Final = "host_port"
ATTR_UNIT_ID: Final = "unit_id"
ATTR_DESCRIPTION: Final = "description"
ATTR_LAST_READ_TIMESTAMP: Final = "last_timestamp"
ATTR_ADDRESS: Final = "address"
#
ATTR_TO_PROPERTY: Final = [
    ATTR_ADDRESS,
    ATTR_DESCRIPTION,
    ATTR_LAST_READ_TIMESTAMP,
    ATTR_UNIT_ID,
    ATTR_HOST_PORT,
]

UPDATE_MIN_TIME: Final = timedelta(seconds=60)
