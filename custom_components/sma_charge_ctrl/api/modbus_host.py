"""The modbus host with everything related like sensors, switches."""
import logging
from typing import Any, Optional

from pymodbus.client import ModbusTcpClient

_LOGGER = logging.getLogger(__name__)


class ModbusHostHub:
    """Modbus Host."""

    _child_sensors: Optional[list[Any]]  # ModbusRegisterSensor

    def __init__(  # noqa: D107
        self, name: str, host: str, port: int, unit_id: int
    ) -> None:
        self._name = name
        self._host = host
        self._port = port
        self._unit_id = unit_id

        self._mdb_cl = ModbusTcpClient(
            host=self._host,
            port=self._port,
            timeout=30.0,
            debug=False,
        )

    @property
    def name(self) -> str:  # noqa: D102
        return self._name

    @property
    def host(self) -> str:  # noqa: D102
        return self._host

    @property
    def port(self) -> int:  # noqa: D102
        return self._port

    @property
    def unit_id(self) -> int:  # noqa: D102
        return self._unit_id

    @property
    def mdb_cl(self) -> ModbusTcpClient:  # noqa: D102
        return self._mdb_cl

    @property
    def child_sensors(self) -> list[Any]:  # noqa: D102
        return self._child_sensors

    @child_sensors.setter
    def child_sensors(self, value):
        self._child_sensors = value

    # async def async_update(self):
    #     """Update all chiild sensors."""
    #     _LOGGER.debug("ModbusHostHub.async_update")
    #     if self._child_sensors is not None:
    #         for child in self._child_sensors:
    #             await child.async_central_update(self.mdb_cl)
