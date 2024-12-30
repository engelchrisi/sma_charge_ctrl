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

        # 802???
        return Api._execute_cmd(client, unit_id, max_chrg, 0)

    @staticmethod
    def battery_start_charging_from_pv(client: ModbusTcpClient, unit_id: int):
        """Start the battery loading from PV + discharging."""

        max_chrg = Api.max_charge_power_battery
        max_dischrg = Api.max_discharge_power_battery

        return Api._execute_cmd(client, unit_id, max_chrg, max_dischrg, 803)

    @staticmethod
    def battery_stop_charging_from_net(
            client: ModbusTcpClient, unit_id: int, discharge_power: int = None
    ):
        """Stop the battery loading from net."""

        return Api._execute_cmd(client, unit_id, 0, discharge_power)

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

        return Api._execute_cmd(client, unit_id, max_chrg, max_dischrg, 803)

    @staticmethod
    def battery_stop_discharging(client: ModbusTcpClient, unit_id: int):
        """Stop the battery discharging its energy."""

        max_chrg = Api.max_charge_power_battery
        max_dischrg = 0

        # Feb-04: Stops discharging for ~10 min without FedInSpntCom_value param!
        # Feb-04: Stops discharging forever  with FedInSpntCom_value=802 !!!
        return Api._execute_cmd(client, unit_id, max_chrg, max_dischrg, 802)

    # noinspection PyPep8Naming
    @staticmethod
    def _execute_cmd(
            client: ModbusTcpClient, unit_id: int,
            max_chrg: int,
            max_dischrg: int,
            FedInSpntCom_value: int = None
    ) -> None:
        """

        @param client:
        @param unit_id:
        @param max_chrg:
        @param max_dischrg:
        @param FedInSpntCom_value: 802 aktiv, 803 inaktiv.
        """
        # Open the connection
        connected = client.connect()
        if not connected:
            _LOGGER.error("Connect to Modbus device not possible")
            return

        # https://www.photovoltaikforum.com/thread/142863-prognosebasierte-ladung-mittels-iobroker/?postID=2001815#post2001815
        # Na klar, also die folgenden 6 Register müssen zyklisch beschrieben werden.
        # Normalbetrieb: 40236 = 2424 (Steuerregister) ; 40793 = 0 (laden min) ; 40795 = 2500 (laden Max) ;
        #                40797 = 0 (entladen min) ; 40799 = 2500 (entladen Max) ; 40801 = immer 0 (Netzausgleichsleistung)
        # Ladung stoppen: 40795 = auf 0 setzen. Das Laden stoppt und das Netzrelais geht nach ein paar Minuten aus.

        # 1. 40236 = 2424 (Steuerregister)
        register = U32(
            40236,
            unit_id,
            "CmpBMSOpMod",
            "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]",
        )
        # register = U32(41259, "CmpBMSOpMod", unit_id, "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]")
        # value_to_write = 308  # Ein(On)
        # value_to_write = 1438  # Automatik(Auto)
        # value_to_write = 2289  # Batterie laden(BatChaMod)
        # value_to_write= 2290 # Batterie entladen(BatDschMod)
        value_to_write = 2424  # Voreinstellung(Dft)
        register.write_value(client, value_to_write)

        # 2./3. 40793 = 0 (laden min) ; 40795 = 2500 (laden Max)
        register = U32(40793, unit_id, "BatChaMinW", "Minimale Batterieladeleistung, in W [WO]")
        register.write_value(client, 0)
        register = U32(
            40795, unit_id, "BatChaMaxW", "Maximale Batterieladeleistung, in W [WO]"
        )
        register.write_value(client, max_chrg)

        time.sleep(1)  # s

        # 4./5. 40797 = 0 (entladen min) ; 40799 = 2500 (entladen Max)
        register = U32(40797, unit_id, "BatDschMinW", "Minimale Batterieentladeleistung, in W [WO]")
        register.write_value(client, 0)
        register = U32(
            40799, unit_id, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"
        )
        register.write_value(client, max_dischrg)

        # 6. 0801 = immer 0 (Netzausgleichsleistung)
        register = S32(40801, unit_id, "GridWSpt", "Sollwert der Netzaustauschleistung, in W [WO]")
        register.write_value(client, 0)  # immmer 0

        time.sleep(1)  # s

        if FedInSpntCom_value is not None:
            register = U32(
                40151,
                unit_id,
                "FedInSpntCom",
                "Wirk- und Blindleistungsregelung über Kommunikation [WO]",
            )
            value_to_write = FedInSpntCom_value
            register.write_value(client, value_to_write)

        # noinspection PyUnreachableCode
        if False:
            # TODO: max_chrg * (253 / 230);              //max power bei 253V
            pwr_at_com = -max_chrg
            register = S32(40149, unit_id, "FedInPwrAtCom", "Wirkleistungsvorgabe [WO]")
            register.write_value(client, pwr_at_com)  # min -3680

        # Close the connection
        client.close()
