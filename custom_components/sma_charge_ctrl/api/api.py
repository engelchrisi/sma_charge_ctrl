"""sma charge ctrl sensor platform."""
# s. /workspaces/ha-core/homeassistant/components/demo/switch.py
import logging
import time

from pymodbus.client import ModbusTcpClient

from .register import S32, U32

_LOGGER = logging.getLogger(__name__)


class Api:  # noqa: D101
    max_charge_power_battery: int = 0
    max_discharge_power_battery: int = 0

    @staticmethod
    def get_default_values(client: ModbusTcpClient, unit_id: int):
        """Read default values ones from WR."""

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        register = U32(
            40189, 3, "WMaxCha", "Maximale Ladeleistung des Batteriestellers, in W [RO]"
        )
        Api.max_charge_power_battery = register.read_value(client).value

        register = U32(
            40191,
            unit_id,
            "WMaxDsch",
            "Maximale Entladeleistung des Batteriestellers, in W [RO]",
        )
        Api.max_discharge_power_battery = register.read_value(client).value

        # Close the connection
        client.close()

        _LOGGER.debug(
            "max_charge_power_battery=%iW, max_discharge_power_battery=%iW",
            Api.max_charge_power_battery,
            Api.max_discharge_power_battery,
        )

    @staticmethod
    def battery_start_charging_from_net(
            client: ModbusTcpClient, unit_id: int, charge_power: int = None
    ):
        """Start the battery loading from net."""

        max_chrg = (
            charge_power
            if charge_power is not None
               and 0 <= charge_power < Api.max_charge_power_battery
            else Api.max_charge_power_battery
        )

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        # register = U32(
        #     40236,
        #     unit_id,
        #     "CmpBMSOpMod",
        #     "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]",
        # )
        # # register = U32(41259, "CmpBMSOpMod", unit_id, "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]")
        # # value_to_write= 308   # Ein(On)
        # # value_to_write = 1438  # Automatik(Auto)
        # value_to_write = 2289 # Batterie laden(BatChaMod)
        # # value_to_write= 2290 # Batterie entladen(BatDschMod)
        # # value_to_write = 2424 # Voreinstellung(Dft)
        # register.write_value(client, value_to_write)

        register = U32(
            40795, unit_id, "BatChaMaxW", "Maximale Batterieladeleistung, in W [WO]"
        )
        register.write_value(client, max_chrg)
        _LOGGER.info("%s:=%i", register.name, max_chrg)
        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )
        register.write_value(client, 0)
        _LOGGER.info("%s:=%i", register.name, 0)

        time.sleep(1)  # s

        register = U32(
            40151,
            unit_id,
            "FedInSpntCom",
            "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
        )
        value_to_write = 802  # aktiv
        register.write_value(client, value_to_write)
        _LOGGER.info("%s:=%i", register.name, value_to_write)

        # TODO: max_chrg * (253 / 230);              //max power bei 253V
        pwr_at_com = -max_chrg
        register = S32(40149, unit_id, "FedInPwrAtCom", "Wirkleistungsvorgabe [WO]")
        register.write_value(client, pwr_at_com)  # min -3680
        _LOGGER.info("%s:=%i", register.name, pwr_at_com)

        # Close the connection
        client.close()

    @staticmethod
    def battery_start_charging_from_pv(client: ModbusTcpClient, unit_id: int):
        """Start the battery loading from PV + discharging."""

        max_chrg = Api.max_charge_power_battery
        max_dischrg = Api.max_discharge_power_battery

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
        # register = U32(41259, unit_id, "CmpBMSOpMod", unit_id, "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]")
        # value_to_write = 308  # Ein(On)
        # value_to_write = 1438  # Automatik(Auto) => Note: only for 5 min.
        # value_to_write = 2289  # Batterie laden(BatChaMod)
        # value_to_write= 2290 # Batterie entladen(BatDschMod)
        value_to_write = 2424  # Voreinstellung(Dft)
        register.write_value(client, value_to_write)

        register = U32(
            40795, unit_id, "BatChaMaxW", "Maximale Batterieladeleistung, in W [WO]"
        )
        register.write_value(client, max_chrg)
        _LOGGER.debug("%s:=%i", register.name, max_chrg)
        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )
        register.write_value(client, max_dischrg)
        _LOGGER.info("%s:=%i", register.name, max_dischrg)

        time.sleep(1)  # s

        # register = U32(
        #     40151,
        #     unit_id,
        #     "FedInSpntCom",
        #     "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
        # )
        #
        # value_to_write = 802  # aktiv
        # register.write_value(client, value_to_write)
        # _LOGGER.debug("%s:=%i", register.name, value_to_write)
        #
        # time.sleep(1)  # s

        # # TODO: max_chrg * (253 / 230);              //max power bei 253V
        # pwr_at_com = max_chrg  # <<<<<<<<<<<<<<
        # register = S32(40149, unit_id, "FedInPwrAtCom", "Wirkleistungsvorgabe [WO]")
        # register.write_value(client, pwr_at_com)  # min -3680
        # _LOGGER.debug("%s:=%i", register.name, pwr_at_com)

        # Close the connection
        client.close()

    @staticmethod
    def battery_stop_charging_from_net(
            client: ModbusTcpClient, unit_id: int, discharge_power: int = None
    ):
        """Stop the battery loading from net."""

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        register = U32(
            40795, unit_id, "BatChaMaxW", "Maximale Batterieladeleistung, in W [WO]"
        )
        register.write_value(client, 0)
        _LOGGER.info("%s:=%i", register.name, 0)

        time.sleep(1)  # s

        register = U32(
            40151,
            unit_id,
            "FedInSpntCom",
            "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
        )

        # Close the connection
        client.close()
        time.sleep(1)  # s

        if discharge_power > 0:
            Api.battery_start_discharging(client, unit_id, discharge_power)
        else:
            Api.battery_stop_discharging(client, unit_id)

    @staticmethod
    def battery_start_discharging(
            client: ModbusTcpClient, unit_id: int, discharge_power: int = None
    ):
        """Allow the battery to discharge its energy."""

        max_chrg = 0
        max_dischrg = (
            discharge_power
            if discharge_power is not None
               and 0 <= discharge_power < Api.max_discharge_power_battery
            else Api.max_discharge_power_battery
        )

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        register = U32(
            40795, unit_id, "BatChaMaxW", "Maximale Batterieladeleistung, in W [WO]"
        )
        register.write_value(client, max_chrg)
        _LOGGER.info("%s:=%i", register.name, max_chrg)
        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )
        register.write_value(client, max_dischrg)
        _LOGGER.info("%s:=%i", register.name, max_dischrg)

        time.sleep(1)  # s

        register = U32(
            40151,
            unit_id,
            "FedInSpntCom",
            "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
        )
        value_to_write = 803  # 803 inaktiv !!!
        register.write_value(client, value_to_write)
        _LOGGER.info("%s:=%i", register.name, value_to_write)

        # Close the connection
        client.close()

    @staticmethod
    def battery_stop_discharging(client: ModbusTcpClient, unit_id: int):
        """Stop the battery discharging its energy."""
        max_dischrg = 0

        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )
        register.write_value(client, max_dischrg)
        _LOGGER.info("%s:=%i", register.name, max_dischrg)

        time.sleep(1)  # s

        register = U32(
            40151,
            unit_id,
            "FedInSpntCom",
            "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
        )
        value_to_write = 802  # 802 aktiv, 803 inaktiv
        register.write_value(client, value_to_write)
        _LOGGER.info("%s:=%i", register.name, value_to_write)

        register = S32(40149, unit_id, "FedInPwrAtCom", "Wirkleistungsvorgabe [WO]")
        pwr_at_com = max_dischrg
        register.write_value(client, pwr_at_com)  # max 3680
        _LOGGER.info("%s:=%i", register.name, pwr_at_com)

        # Close the connection
        client.close()
