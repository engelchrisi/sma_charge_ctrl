"""sma charge ctrl sensor platform."""
# s. /workspaces/ha-core/homeassistant/components/demo/switch.py
import logging
import time

from pymodbus.client import ModbusTcpClient

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .modbus_host import ModbusHostHub
from .Register import S32, U32

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the demo switch platform."""
    _LOGGER.debug("switch.async_setup_entry")
    hub: ModbusHostHub = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        [
            SmaChargingSwitch("Charge from Net", hub.mdb_cl, hub.unit_id),
            SmaDischargingSwitch("Discharge Battery", hub.mdb_cl, hub.unit_id),
        ]
    )


class SmaSwitchBase(SwitchEntity):
    """Base class."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(self, name, pymodbus_client: ModbusTcpClient, unit_id: int) -> None:  # noqa: D107
        self._name = name
        self._pymodbus_client = pymodbus_client
        self._unit_id = unit_id

        self._attr_name = name
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

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._attr_is_on = False
        self.schedule_update_ha_state()


class SmaChargingSwitch(SmaSwitchBase):
    """Class to switch on/off charging."""

    _attr_is_on = False

    # @property
    # def name(self):  # noqa: D102
    #     return self._name

    @property
    def is_on(self):  # noqa: D102
        return bool(self._attr_is_on)

    def turn_on(self, **kwargs):
        """Turn the device on."""
        super().turn_on()
        _LOGGER.debug("Charging turned ON")
        self.start_charging_from_net()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        super().turn_off()
        _LOGGER.debug("Charging turned OFF")
        self.stop_charging_from_net(allow_discharge=True)

    def start_charging_from_net(self):
        """Ladevorgang der Batterie vom Netz starten."""
        client = self._pymodbus_client
        unit_id = self._unit_id

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        register = U32(
            40236,
            unit_id,
            "CmpBMSOpMod",
            "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]",
        )
        # register = U32(41259, "CmpBMSOpMod", unit_id, "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]")
        # value_to_write= 308   # Ein(On)
        # value_to_write = 1438  # Automatik(Auto)
        value_to_write = 2289  # Batterie laden(BatChaMod)
        # value_to_write= 2290  # Batterie entladen(BatDschMod)
        # value_to_write = 2424  # Voreinstellung(Dft)
        register.write_value(client, value_to_write)

        register = U32(
            40795,
            unit_id,
            "BatChaMaxW",
            "Maximale Batterieladeleistung, in W [WO]",
        )
        value_to_write = 3680
        register.write_value(client, value_to_write)

        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )
        value_to_write = 0
        register.write_value(client, value_to_write)

        time.sleep(1)  # s

        # register = U32(40793, unit_id, "BatChaMinW", "Minimale Batterieladeleistung, in W [WO]")
        # value_to_write = 0
        # register.write_value(client, value_to_write)
        #
        # time.sleep(1)  # s
        #
        # register = U32(40797, unit_id, "BatDschMinW", "Minimale Batterieentladeleistung, in W [WO]")
        # value_to_write = 0
        # register.write_value(client, value_to_write)
        #
        # time.sleep(1)  # s
        #
        # register = S32(40801, unit_id, "GridWSpt", "Sollwert der Netzaustauschleistung, in W [WO]")
        # value_to_write = 0
        # register.write_value(client, value_to_write)

        register = U32(
            40151,
            unit_id,
            "FedInSpntCom",
            "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
        )
        value_to_write = 802  # aktiv
        register.write_value(client, value_to_write)

        # pwrAtCom_def = 3680 * (253 / 230)  # max power bei 253V
        register = S32(40149, unit_id, "FedInPwrAtCom", "Wirkleistungsvorgabe [WO]")
        value_to_write = -1500  # -3680
        register.write_value(client, value_to_write)

        # Close the connection
        client.close()

    def stop_charging_from_net(self, allow_discharge: bool):
        """Ladevorgang beenden, Entladevorgang der Batterie erlauben."""
        client = self._pymodbus_client
        unit_id = self._unit_id

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        register = U32(
            40236,
            unit_id,
            "CmpBMSOpMod",
            "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]",
        )

        # register = U32(41259, unit_id, "CmpBMSOpMod", "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]")
        # value_to_write= 308   # Ein(On)
        value_to_write = 1438  # Automatik(Auto)
        # value_to_write = 2289  # Batterie laden(BatChaMod)
        # value_to_write= 2290  # Batterie entladen(BatDschMod)
        # value_to_write = 2424  # Voreinstellung(Dft)
        register.write_value(client, value_to_write)

        register = U32(
            40795, unit_id, "BatChaMaxW", "Maximale Batterieladeleistung, in W [WO]"
        )
        value_to_write = 3680
        register.write_value(client, value_to_write)

        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )
        value_to_write = 3680 if allow_discharge else 0
        register.write_value(client, value_to_write)

        time.sleep(1)  # s

        register = U32(
            40151,
            unit_id,
            "FedInSpntCom",
            "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
        )
        value_to_write = 803  # 802 aktiv, 803 inaktiv
        register.write_value(client, value_to_write)

        # Close the connection
        client.close()


class SmaDischargingSwitch(SmaSwitchBase):
    """Class to switch on/off charging."""

    _attr_is_on = True

    # @property
    # def name(self):  # noqa: D102
    #     return self._name

    @property
    def is_on(self):  # noqa: D102
        return bool(self._attr_is_on)

    def turn_on(self, **kwargs):
        """Turn the device on."""
        super().turn_on()
        _LOGGER.debug("Discharging turned ON")
        self.start_discharging()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        super().turn_off()
        _LOGGER.debug("Discharging turned OFF")
        self.stop_discharging()

    def start_discharging(self):
        """Entladevorgang der Batterie verbieten."""
        return self.set_battery_discharge_power(3680)

    def stop_discharging(self):
        """Entladevorgang der Batterie verbieten."""
        return self.set_battery_discharge_power(0)

    def set_battery_discharge_power(self, value_to_write: int):  # noqa: D102
        client = self._pymodbus_client
        unit_id = self._unit_id

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )

        register.write_value(client, value_to_write)

        # Close the connection
        client.close()
