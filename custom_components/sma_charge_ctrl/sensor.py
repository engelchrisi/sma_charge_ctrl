"""sma charge ctrl sensor platform."""
import logging
from datetime import timedelta, datetime
from typing import  Callable, Optional
from Register import U32, S32, U64
from pymodbus.client.sync import ModbusTcpClient
import voluptuous as vol


from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
)
CONF_UNIT_ID = "unit_id"
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.typing import (
    ConfigType,
    DiscoveryInfoType,
    HomeAssistantType,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Required(CONF_UNIT_ID): cv.positive_int,
    }
)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    """Set up the sensor platform."""
    # session = async_get_clientsession(hass)
    unit_id = config[CONF_UNIT_ID]
    modbus_client = ModbusClientSensor(config[CONF_HOST], config[CONF_PORT], unit_id)
    pymodbus_client= modbus_client.modbus_client
    sensors = [
                ModbusRegisterSensor(pymodbus_client, U32(30053, unit_id, "DevTypeId", "Gerätetyp")),
                ModbusRegisterSensor(pymodbus_client, U32(31393, unit_id, "BatChrg.CurBatCha", "Momentane Batterieladung")) 
              ]
    async_add_entities(sensors, update_before_add=True)


class ModbusClientSensor(Entity):
    def __init__(self, host: str, port: int, unit_id: int):
        super().__init__()
        self.host = host
        self.port = port
        self.unit_id = unit_id
        # SBS_IP = "192.168.178.56"
        self.pymodbus_client = ModbusTcpClient(self.host, port=self.port, timeout=30.0, debug=True)        

    @property
    def pymodbus_client(self) -> ModbusTcpClient:
        return self.pymodbus_client
    
class ModbusRegisterSensor(Entity):
    """Representation of a register specific sensor."""

    def __init__(self, pymodbus_client: ModbusTcpClient, register: Register):
        super().__init__()

        self._pymodbus_client= pymodbus_client
        self._register= register
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._register.name

    @property
    def state(self) -> Optional[str]:
        return self._register.last_value

    @property
    def last_timestamp(self) -> Optional[datetime]:
        return self._register.last_value
    
    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available    

    async def async_update(self):
        try:
            _LOGGER.debug("==> ModbusReader.update")            
            # self._register.read_value(self._pymodbus_client)
            self._available = True            
        except Exception as e:
            self._available = False
            _LOGGER.exception(e)


