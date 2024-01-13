"""The register definition."""

from collections.abc import Mapping
import logging
from typing import Any, Optional

from pymodbus.client import ModbusTcpClient

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN

from .const import (
    ATTR_ADDRESS,
    ATTR_DESCRIPTION,
    ATTR_HOST_PORT,
    ATTR_TO_PROPERTY,
    ATTR_UNIT_ID,
)
from .Register import ModbusRegisterBase

_LOGGER = logging.getLogger(__name__)


class ModbusRegisterSensor(SensorEntity):
    """Representation of a register specific sensor."""

    _unrecorded_attributes = frozenset(
        {ATTR_ADDRESS, ATTR_DESCRIPTION, ATTR_UNIT_ID, ATTR_HOST_PORT}
    )

    def __init__(
        self,
        hub_name: str,
        pymodbus_client: ModbusTcpClient,
        register: ModbusRegisterBase,
        device_class: SensorDeviceClass = SensorDeviceClass.VOLTAGE,
        unit_of_measurement: str = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__()

        self._register = register
        self._hub_name = hub_name
        self._pymodbus_client = pymodbus_client
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

        # A unique_id for this entity with in this domain. This means for example if you
        # have a sensor on this cover, you must ensure the value returned is unique,
        # which is done here by appending "_cover". For more information, see:
        # https://developers.home-assistant.io/docs/entity_registry_index/#unique-id-requirements
        # Note: This is NOT used to generate the user visible Entity ID used in automations.
        self._attr_unique_id = register.name + " " + hub_name

        # This is the name for this *entity*, the "name" attribute from "device_info"
        # is used as the device name for device screens in the UI. This name is used on
        # entity screens, and used to build the Entity ID that's used is automations etc.
        self._attr_name = register.description + " " + hub_name

        self._attr_native_value = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        # self._attr_icon = None
        #
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

    async def async_update(self):
        """Re-read via modbus."""
        value = self._register.read_value(self._pymodbus_client)
        self._attr_native_value = value.value if value is not None else None
        self.last_timestamp = self._register.last_timestamp
        _LOGGER.debug(
            "ModbusReader.async_central_update %s: Read Value: %s %s",
            self.name,
            self._attr_native_value,
            self._attr_native_unit_of_measurement,
        )
