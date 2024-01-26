# Rename sma_charg_ctrl/__init__.py to *.bak in order to test without Homeassistant environment
import logging
from unittest import TestCase

from pymodbus.client import ModbusTcpClient

from custom_components.sma_charge_ctrl.api.api import Api

_LOGGER = logging.getLogger(__name__)


class TestApi(TestCase):
    SBS_IP = "192.168.178.56"
    UNIT_ID = 3

    @staticmethod
    def înit_logger():
        # Set the logging level (optional, default is WARNING)
        _LOGGER.setLevel(logging.DEBUG)

        # Create a handler that writes log messages to sys.stdout
        stdout_handler = logging.StreamHandler(sys.stdout)

        # Create a formatter (optional)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stdout_handler.setFormatter(formatter)

        # Add the handler to the logger
        _LOGGER.addHandler(stdout_handler)

    def test_battery_start_charge_1500(self):
        """load battery from net with 1500W"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        charge_power = 1500  # max 3680
        Api.battery_start_charging_from_net(client, self.UNIT_ID, charge_power)

    def test_battery_start_charge_max(self):
        """load battery from net with max W"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_start_charging_from_net(client, self.UNIT_ID)

    def test_battery_start_charge_from_pv(self):
        """load battery from net with max W"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_start_charging_from_pv(client, self.UNIT_ID)

    def test_battery_start_charge_0(self):
        """load battery from net with 0W"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        charge_power = 0
        Api.battery_start_charging_from_net(client, self.UNIT_ID, charge_power)

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

    def test_battery_stop_discharging(self):
        """S. above"""
        client = ModbusTcpClient(TestApi.SBS_IP, port=502, timeout=30.0, debug=True)
        Api.get_default_values(client, self.UNIT_ID)
        Api.battery_stop_discharging(client, self.UNIT_ID)
