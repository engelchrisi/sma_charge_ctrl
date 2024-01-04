from datetime import datetime
from typing import Optional

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder, BinaryPayloadBuilder


class ValueWithTimestamp:
    _date: datetime
    _value: any

    def __init__(self, value: any):
        self._date = datetime.now()  # datetime.timestamp(datetime.now())
        self._value = value

    @property
    def value(self) -> any:
        return self._value

    @property
    def timestamp(self) -> datetime:
        return self._date

    def __str__(self):
        return f"{self._value} from {self._date}"


class Register:
    length: int
    id: int
    slave_id: int
    value: Optional[ValueWithTimestamp]

    def __init__(self, reg_id: int, slave_id: int, name: str, description: str, length: int):
        self.id = reg_id
        self.slave_id = slave_id
        self.name = name
        self.description = description
        self.length = length
        self.value = None

    def __str__(self):
        return f"{self.id} {self.name} ({self.description}): {self.last_value}"

    @property
    def last_value(self) -> Optional[any]:
        return self.value.value if self.value is not None else None

    @property
    def last_timestamp(self) -> Optional[datetime]:
        return self.value.timestamp if self.value is not None else None

    def read_value(self, client: ModbusTcpClient) -> ValueWithTimestamp:
        response = client.read_input_registers(self.id, self.length, self.slave_id)

        if response.isError():
            print(f"Error response: {response}")
            return None
        else:
            registers = response.registers
            val = self._decode_value(registers)
            self.value = ValueWithTimestamp(val)
            return self.value

    def write_value(self, client: ModbusTcpClient, value_to_write) -> bool:
        registers = self._encode_value(value_to_write)
        response = client.write_registers(self.id, values=registers, slave=self.slave_id)

        if response.isError():
            print(f"Error response: {response}")
            return False
        else:
            return True

    def is_null(self):
        return None

    def _encode_value(self, value_to_write) -> []:
        return None

    def _decode_value(self, registers: []):
        return None


class S16(Register):
    def __init__(self, register_id: int, slave_id: int, name: str, description: str):
        Register.__init__(self, register_id, slave_id, name, description, 1)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_16bit_int(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG).decode_16bit_int()

    def is_null(self):
        return self._decode_value() == 0x8000


class S32(Register):
    def __init__(self, register_id: int, slave_id: int, name: str, description: str):
        Register.__init__(self, register_id, slave_id, name, description, 2)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_32bit_int(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG).decode_32bit_int()

    def is_null(self):
        return self.last_value == 0x80000000


class U16(Register):
    def __init__(self, register_id: int, slave_id: int, name: str, description: str):
        Register.__init__(self, register_id, slave_id, name, description, 1)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_16bit_uint(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG).decode_16bit_uint()

    def is_null(self):
        return self.last_value == 0xFFFF


class U32(Register):
    def __init__(self, register_id: int, slave_id: int, name: str, description: str):
        Register.__init__(self, register_id, slave_id, name, description, 2)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_32bit_uint(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG).decode_32bit_uint()

    def is_null(self):
        return self.last_value == 0xFFFFFFFF or self.last_value == 0xFFFFFD


class U64(Register):
    def __init__(self, register_id: int, slave_id: int, name: str, description: str):
        Register.__init__(self, register_id, slave_id, name, description, 4)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_64bit_uint(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG).decode_64bit_uint()

    def is_null(self):
        return self.last_value == 0xFFFFFFFFFFFFFFFF


class STR32(Register):
    def __init__(self, register_id: int, slave_id: int, name: str, description: str):
        Register.__init__(self, register_id, slave_id, name, description, 8)

    def _encode_value(self, value_to_write) -> []:
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_string(value_to_write)
        # Get the payload as a byte array
        return builder.to_registers()

    def _decode_value(self, registers: []):
        return BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.BIG).decode_string()

    def is_null(self):
        return self.last_value == ""
