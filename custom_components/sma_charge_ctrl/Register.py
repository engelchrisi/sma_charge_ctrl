"""Register class per modbus type."""
from datetime import datetime
import logging
from typing import Optional

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

_LOGGER = logging.getLogger(__name__)


class ValueWithTimestamp:  # noqa: D101
    _date: datetime
    _value: any

    def __init__(self, value: any) -> None:  # noqa: D107
        self._date = datetime.now()  # datetime.timestamp(datetime.now())
        self._value = value

    @property
    def value(self) -> any:  # noqa: D102
        return self._value

    @property
    def timestamp(self) -> datetime:  # noqa:  D102
        return self._date

    def __str__(self):  # noqa: D105
        return f"{self._value} from {self._date}"


class ModbusRegisterBase:  # noqa: D101
    length: int
    id: int
    slave_id: int
    value: Optional[ValueWithTimestamp]

    def __init__(  # noqa: D107
        self, reg_id: int, slave_id: int, name: str, description: str, length: int
    ) -> None:
        self.id = reg_id
        self.slave_id = slave_id
        self.name = name
        self.description = description
        self.length = length
        self.value = None

    def __str__(self):  # noqa: D105
        return f"{self.id} {self.name} ({self.description}): {self.last_value}"

    @property
    def last_value(self) -> Optional[any]:  # noqa: D102
        return self.value.value if self.value is not None else None

    @property
    def last_timestamp(self) -> Optional[datetime]:  # noqa: D102
        return self.value.timestamp if self.value is not None else None

    def read_value(self, client: ModbusTcpClient) -> ValueWithTimestamp:
        """Actively read via modbus."""
        response = client.read_input_registers(self.id, self.length, self.slave_id)

        if response.isError():
            _LOGGER.error("Error response: %s", str(response))
            return None
        else:
            registers = response.registers
            val = self._decode_value(registers)
            self.value = ValueWithTimestamp(val)
            return self.value

    def write_value(self, client: ModbusTcpClient, value_to_write) -> bool:
        """Write via modbus."""
        registers = self._encode_value(value_to_write)
        response = client.write_registers(
            self.id, values=registers, slave=self.slave_id
        )

        if response.isError():
            _LOGGER.error("Error response: %s", str(response))
            return False
        else:
            return True

    # def is_null(self):
    #     return None

    def _encode_value(self, value_to_write) -> []:
        return None

    def _decode_value(self, registers: []):
        return None


class S16(ModbusRegisterBase):  # noqa: D101
    def __init__(  # noqa: D107
        self, register_id: int, slave_id: int, name: str, description: str
    ) -> None:
        ModbusRegisterBase.__init__(self, register_id, slave_id, name, description, 1)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_16bit_int(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG
        ).decode_16bit_int()

    # def is_null(self):
    #     return self._decode_value() == 0x8000


class S32(ModbusRegisterBase):  # noqa: D101
    def __init__(  # noqa: D107
        self, register_id: int, slave_id: int, name: str, description: str
    ) -> None:
        ModbusRegisterBase.__init__(self, register_id, slave_id, name, description, 2)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_32bit_int(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG
        ).decode_32bit_int()

    # def is_null(self):
    #     return self.last_value == 0x80000000


class U16(ModbusRegisterBase):  # noqa: D101
    def __init__(  # noqa: D107
        self, register_id: int, slave_id: int, name: str, description: str
    ) -> None:
        ModbusRegisterBase.__init__(self, register_id, slave_id, name, description, 1)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_16bit_uint(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG
        ).decode_16bit_uint()

    # def is_null(self):
    #     return self.last_value == 0xFFFF


class U32(ModbusRegisterBase):  # noqa: D101
    def __init__(  # noqa: D107
        self, register_id: int, slave_id: int, name: str, description: str
    ) -> None:
        ModbusRegisterBase.__init__(self, register_id, slave_id, name, description, 2)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_32bit_uint(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG
        ).decode_32bit_uint()

    # def is_null(self):
    #     return self.last_value == 0xFFFFFFFF or self.last_value == 0xFFFFFD


class U64(ModbusRegisterBase):  # noqa: D101
    def __init__(  # noqa: D107
        self, register_id: int, slave_id: int, name: str, description: str
    ) -> None:
        ModbusRegisterBase.__init__(self, register_id, slave_id, name, description, 4)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_64bit_uint(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG
        ).decode_64bit_uint()

    # def is_null(self):
    #     return self.last_value == 0xFFFFFFFFFFFFFFFF


class STR32(ModbusRegisterBase):  # noqa: D101
    def __init__(  # noqa: D107
        self, register_id: int, slave_id: int, name: str, description: str
    ) -> None:
        ModbusRegisterBase.__init__(self, register_id, slave_id, name, description, 8)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_string(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(
            registers, byteorder=Endian.BIG
        ).decode_string()

    # def is_null(self):
    #     return self.last_value == ""
