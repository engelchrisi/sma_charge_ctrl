import logging
from pymodbus.client.sync import ModbusTcpClient
from homeassistant.helpers.entity import Entity
from homeassistant.components.switch import SwitchEntity
from Register import U32, S32, U64

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'sma_charge_ctrl'

def setup_platform(hass, config, add_entities, discovery_info=None):
    entities = []

    SBS_IP = "192.168.178.56"
    modbus_client = ModbusTcpClient(SBS_IP, port=502, timeout=30.0, debug=True)
    _LOGGER.debug("==> ModbusTcpClient created")

    entities.append(SmaChargingSwitch('Charging', modbus_client))
    entities.append(ModbusReader(modbus_client, U32(31393, "BatChrg.CurBatCha", "Momentane Batterieladung [RO]")))

    add_entities(entities)

class ModbusReader(Entity):
    def __init__(self, name, modbus_client: ModbusTcpClient, register: Register):
        self._name = name
        self._state = None
        self._modbus_client = modbus_client
        self._register = register

    @property
    def name(self):
        return self._register.name

    @property
    def state(self):
        return self._register.last_value

    def update(self):
        try:
            _LOGGER.debug("==> ModbusReader.update")            
            # self._register.read_value(self._modbus_client)
        except Exception as e:
            _LOGGER.error("Error updating Modbus entity: %s", e)

class SmaChargingSwitch(SwitchEntity):
    def __init__(self, name, modbus_client: ModbusTcpClient):
        self._name = name
        self._modbus_client = modbus_client
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return bool(self._state)

    def turn_on(self, **kwargs):
        try:
            _LOGGER.debug("==> SmaChargingSwitch.turn_on")            
            self._state = 1
        except Exception as e:
            _LOGGER.error("Error turning on Modbus switch: %s", e)

    def turn_off(self, **kwargs):
        try:
            _LOGGER.debug("==> SmaChargingSwitch.turn_off")            
            self._state = 0
        except Exception as e:
            _LOGGER.error("Error turning off Modbus switch: %s", e)

    def update(self):
        try:
            # Use pymodbus to read the Modbus register value
            result = self._modbus_client.read_input_registers(self._register_address, 1)
            if result.isError():
                _LOGGER.error("Modbus error: %s", result)
            else:
                self._state = result.registers[0]
        except Exception as e:
            _LOGGER.error("Error updating Modbus switch: %s", e)