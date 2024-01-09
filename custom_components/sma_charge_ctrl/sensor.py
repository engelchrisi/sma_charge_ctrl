"""GitHub sensor platform."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import timedelta
import logging
from typing import Any, Optional

# from _sha1 import sha1
from pymodbus.client import ModbusTcpClient
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_UNIQUE_ID,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

from .const import (
    ATTR_ADDRESS,
    ATTR_DESCRIPTION,
    ATTR_HOST_PORT,
    ATTR_TO_PROPERTY,
    ATTR_UNIT_ID,
    CONF_UNIT_ID,
    DEFAULT_NAME,
    DOMAIN,
    UPDATE_MIN_TIME,
)
from .Register import S32, U32, ModbusRegisterBase

_LOGGER = logging.getLogger(__name__)
# Time between updating data from GitHub
SCAN_INTERVAL = timedelta(minutes=10)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_UNIT_ID): cv.positive_int,
    }
)


async def async_setup_entry(  # noqa: D103
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    config = hass.data[DOMAIN][config_entry.entry_id]
    # Update our config to include new repos and remove those that have been removed.
    if config_entry.options:
        config.update(config_entry.options)

    # session = async_get_clientsession(hass)

    unit_id = config[CONF_UNIT_ID]  # noqa: F841
    mdb_cl = ModbusTcpClient(
        host=config[CONF_HOST],
        port=config[CONF_PORT],
        timeout=30.0,
        debug=False,
    )
    if not mdb_cl:
        return False

    sensors = create_sensors(mdb_cl, unit_id)
    async_add_entities(sensors)


async def async_setup_platform(
    hass: core.HomeAssistant,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    # session = async_get_clientsession(hass)

    unit_id = config[CONF_UNIT_ID]  # noqa: F841
    mdb_cl = ModbusTcpClient(
        host=config[CONF_HOST],
        port=config[CONF_PORT],
        timeout=30.0,
        debug=False,
    )
    if not mdb_cl:
        return False

    sensors = create_sensors(mdb_cl, unit_id)
    async_add_entities(sensors)


def create_sensors(mdb_cl: ModbusTcpClient, unit_id: int):  # noqa: D103
    sensors = [
        # ModbusRegisterSensor(
        #     mdb_cl, U32(30053, unit_id, "DevTypeId", "Gerätetyp"), device_class=None
        # ),
        ModbusRegisterSensor(
            mdb_cl,
            S32(30775, unit_id, "PowerAC", "Leistung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_cl,
            U32(30783, unit_id, "GridV1", "Netzspannung Phase L1", scale_factor=0.01),
            device_class=SensorDeviceClass.VOLTAGE,
            unit_of_measurement="V",
        ),
        ModbusRegisterSensor(
            mdb_cl,
            S32(30845, unit_id, "Bat.SOC", "Batterieladezustand"),
            device_class=SensorDeviceClass.BATTERY,
            unit_of_measurement="%",
        ),
        ModbusRegisterSensor(
            mdb_cl,
            S32(30865, unit_id, "TotWIn", "Leistung Bezug"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_cl,
            S32(30867, unit_id, "TotWOut", "Leistung Einspeisung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_cl,
            U32(31007, unit_id, "RmgChaTm", "Restzeit der Batterieladephase"),
            device_class=SensorDeviceClass.DURATION,
            unit_of_measurement="s",
        ),
        ModbusRegisterSensor(
            mdb_cl,
            U32(31393, unit_id, "BatChrg.CurBatCha", "Momentane Batterieladung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_cl,
            U32(31395, unit_id, "BatDsch.CurBatDsch", "Momentane Batterieentladung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        # ModbusRegisterSensor(
        #     mdb_cl,
        #     U64(31397, unit_id, "BatChrg.BatChrg", "Batterieladung"),
        #     device_class=SensorDeviceClass.POWER,
        #     unit_of_measurement="W",
        # ),
        # ModbusRegisterSensor(
        #     mdb_cl,
        #     U64(31401, unit_id, "BatDsch.BatDsch", "Batterieentladung"),
        #     device_class=SensorDeviceClass.POWER,
        #     unit_of_measurement="W",
        # ),
    ]

    return sensors


# s. /workspaces/ha-core/homeassistant/components/demo/sensor.py
class ModbusRegisterSensor(SensorEntity):
    """Representation of a register specific sensor."""

    _unrecorded_attributes = frozenset(
        {ATTR_ADDRESS, ATTR_DESCRIPTION, ATTR_UNIT_ID, ATTR_HOST_PORT}
    )

    def __init__(
        self,
        pymodbus_client: ModbusTcpClient,
        register: ModbusRegisterBase,
        device_class: SensorDeviceClass = SensorDeviceClass.VOLTAGE,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__()

        self._pymodbus_client = pymodbus_client
        self._register = register
        self.address = register.id
        self.description = register.description
        self.last_timestamp = None
        self.unit_id = register.slave_id
        self.host_port = (
            pymodbus_client.comm_params.host
            + ":"
            + str(pymodbus_client.comm_params.port)
        )

        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_name = register.name
        self._attr_native_value = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        # self._attr_icon = None
        self._attr_device_class = None
        #
        self._attr_unique_id = (
            str(register.id) + "_" + register.name + "_" + str(pymodbus_client)
        )
        # str(
        #     sha1(
        #         ";".join([str(register.id), str(register.name)]).encode("utf-8")
        #     ).hexdigest()
        # )

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._attr_name

    @property
    def state(self) -> Optional[str]:
        """Bla."""
        return self._register.last_value

    @staticmethod
    def _has_state(state) -> bool:
        """Return True if state has any value."""
        return state is not None and state not in [
            STATE_UNKNOWN,
            STATE_UNAVAILABLE,
            "None",
            "",
        ]

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._has_state(self._attr_native_value)

    @property
    def extra_state_attributes(self) -> Optional[Mapping[str, Any]]:
        """Return entity specific state attributes."""
        state_attr = {
            attr: getattr(self, attr)
            for attr in ATTR_TO_PROPERTY
            if getattr(self, attr) is not None
        }
        return state_attr

    @Throttle(UPDATE_MIN_TIME)
    async def async_update(self):
        """Re-read via modbus."""
        value = self._register.read_value(self._pymodbus_client)
        self._attr_native_value = value.value if value is not None else None
        self.last_timestamp = self._register.last_timestamp
        _LOGGER.debug(
            "ModbusReader.update %s: Read Value: %s %s",
            self.name,
            self._attr_native_value,
            self._attr_native_unit_of_measurement,
        )
