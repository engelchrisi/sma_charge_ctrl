# Rename sma_charg_ctrl/__init__.py to *.BAK in order to test without Homeassistant environment
import logging
from unittest import TestCase

from pymodbus.client import ModbusTcpClient

from test import logging_config

# Note: Initialize logging configuration before importing sma_charge_ctrl Api!
logging_config.setup_logging()

from custom_components.sma_charge_ctrl.api.api import Api

_LOGGER = logging.getLogger(__name__)


# HM: Das prog. basierte Laden muss dann ABgeschaltet werden, weil das die Skripte bzw. ioBroker übernehmen

# https://www.photovoltaikforum.com/thread/142863-prognosebasierte-ladung-mittels-iobroker/?postID=2001815#post2001815
# Na klar, also die folgenden 6 Register müssen zyklisch beschrieben werden.
# Normalbetrieb: 40236 = 2424 (Steuerregister) ; 40793 = 0 (laden min) ; 40795 = 2500 (laden Max) ;
#                40797 = 0 (entladen min) ; 40799 = 2500 (entladen Max) ; 40801 = immer 0 (Netzausgleichsleistung)
# Ladung stoppen: 40795 = auf 0 setzen. Das Laden stoppt und das Netzrelais geht nach ein paar Minuten aus.
# DC-Schütz ausschalten: 40236 = auf 2290 setzen. Das Schütz geht nach ein paar Minuten aus.
# WR wieder einschalten: Die Werte wieder auf Normalbetrieb setzen.
# Ladeleistung reduzieren: 40795 = auf z.B. 1500 setzen.
#
# Das klappt mit dem SBS 5.0, wahrscheinlich auch mit dem 2.5! Ich würde das erst mal mit einen Skript in Blockly testen. 6 Datenpunkte erstellen,
# in den unsere oben genannten Registerwerte kommen. Das Skript wird alle 15 Sekunden aufgerufen und überträgt die Daten in die Modbusdatenpunkte.
# Aber bitte den Steuerbefehl benutzen, sonst werden die Daten nicht in den WR übertragen...

class TestApi(TestCase):
    SBS_IP = "192.168.178.56"
    UNIT_ID = 3

    def test_logging(self):
        _LOGGER.info("This is an info trace.")

    # Feb-04: working for ~30 min
    def test_battery_start_charge_1500(self):
        """load battery from net with 1500W"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        charge_power = 1500  # max 3680
        Api.battery_start_charging_from_net(client, self.UNIT_ID, charge_power)

    # Feb-04: working for ~30 min
    def test_battery_start_charge_max(self):
        """load battery from net with max W"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_start_charging_from_net(client, self.UNIT_ID)

    # Feb-04: Starts discharging
    # TODO: test charging from PV
    def test_battery_start_charge_from_pv(self):
        """load battery from net with max W"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_start_charging_from_pv(client, self.UNIT_ID)

    def test_battery_stop_charging_no_discharge(self):
        """No further battery loading from net but NO discharging"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        discharge_power = 0
        Api.battery_stop_charging_from_net(client, self.UNIT_ID, discharge_power)

    def test_battery_stop_charging_with_discharge(self):
        """No further battery loading from net and discharging"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_stop_charging_from_net(client, self.UNIT_ID)

    def test_battery_start_discharging(self):
        """S. above"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_start_discharging(client, self.UNIT_ID)

    # Feb-04: working
    def test_battery_stop_discharging(self):
        """S. above"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_stop_discharging(client, self.UNIT_ID)
