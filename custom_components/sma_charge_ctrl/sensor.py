# noqa: D102
"""sma charge ctrl sensor platform."""
from collections.abc import Mapping
import logging
from typing import Any, Optional

# from _sha1 import sha1
from pymodbus.client import ModbusTcpClient
import voluptuous as vol

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_UNIQUE_ID,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import Throttle

from .const import (
    ATTR_ADDRESS,
    ATTR_DESCRIPTION,
    ATTR_HOST_PORT,
    ATTR_TO_PROPERTY,
    ATTR_UNIT_ID,
    DEFAULT_NAME,
    DOMAIN,
    UPDATE_MIN_TIME,
)
from .Register import S32, U32, ModbusRegisterBase

_LOGGER = logging.getLogger(__name__)

CONF_UNIT_ID = "unit_id"
PLATFORM_SCHEMA = vol.All(
    PLATFORM_SCHEMA.extend(
        {
            vol.Optional(CONF_UNIQUE_ID): cv.string,
            vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            vol.Required(CONF_HOST): cv.string,
            vol.Required(CONF_PORT): cv.port,
            vol.Required(CONF_UNIT_ID): cv.positive_int,
        }
    )
)


# setting up the sensors from UI (config_flow.py)
# s. https://aarongodfrey.dev/home%20automation/building_a_home_assistant_custom_component_part_3/
# async def async_setup_entry(
#     hass: HomeAssistant, entry: config_entries.ConfigEntry
# ) -> bool:
#     """Set up platform from a ConfigEntry."""
#     hass.data.setdefault(DOMAIN, {})
#     hass_data = dict(entry.data)
#     # Registers update listener to update config entry when options are updated.
#     unsub_options_update_listener = entry.add_update_listener(options_update_listener)
#     # Store a reference to the unsubscribe function to cleanup if an entry is unloaded.
#     hass_data["unsub_options_update_listener"] = unsub_options_update_listener
#     hass.data[DOMAIN][entry.entry_id] = hass_data


# pylint: disable=unused-argument
async def async_setup_platform(
    hass: HomeAssistant, config, async_add_entities, discovery_info=None
):
    """Set up the sensor platform."""
    # session = async_get_clientsession(hass)
    unit_id = config[CONF_UNIT_ID]
    mdb_cl = ModbusTcpClient(
        host=config[CONF_HOST], port=config[CONF_PORT], timeout=30.0, debug=False
    )
    sensors = [
        SmaChargingSwitch("SMA Charge Switch", mdb_cl),
        # --------------------------------------------
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
    async_add_entities(sensors, update_before_add=True)


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
