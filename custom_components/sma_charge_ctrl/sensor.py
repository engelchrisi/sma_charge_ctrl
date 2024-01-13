"""Sma Charge Ctrl sensor platform."""
from __future__ import annotations

import logging

from homeassistant import config_entries, core
from homeassistant.components.sensor import SensorDeviceClass

from .const import DOMAIN
from .modbus_host import ModbusHostHub
from .modbus_register_sensor import ModbusRegisterSensor
from .Register import S32, U32

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(  # noqa: D103
    hass: core.HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
) -> None:
    """Set up sensors."""
    _LOGGER.debug("sensor.async_setup_entry")
    hub: ModbusHostHub = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = create_sensors(hub)
    async_add_entities(new_devices)


def create_sensors(mdb_host: ModbusHostHub):  # noqa: D103
    mdb_cl = mdb_host.mdb_cl
    unit_id: int = mdb_host.unit_id
    sensors = [
        # ModbusRegisterSensor(
        #     mdb_host.name, mdb_cl, U32(30053, unit_id, "DevTypeId", "Gerätetyp"), device_class=None
        # ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            S32(30775, unit_id, "PowerAC", "Leistung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            U32(30783, unit_id, "GridV1", "Netzspannung Phase L1", scale_factor=0.01),
            device_class=SensorDeviceClass.VOLTAGE,
            unit_of_measurement="V",
        ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            S32(30845, unit_id, "Bat.SOC", "Batterieladezustand"),
            device_class=SensorDeviceClass.BATTERY,
            unit_of_measurement="%",
        ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            S32(30865, unit_id, "TotWIn", "Leistung Bezug"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            S32(30867, unit_id, "TotWOut", "Leistung Einspeisung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            U32(31007, unit_id, "RmgChaTm", "Restzeit der Batterieladephase"),
            device_class=SensorDeviceClass.DURATION,
            unit_of_measurement="s",
        ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            U32(31393, unit_id, "BatChrg.CurBatCha", "Momentane Batterieladung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        ModbusRegisterSensor(
            mdb_host.name,
            mdb_cl,
            U32(31395, unit_id, "BatDsch.CurBatDsch", "Momentane Batterieentladung"),
            device_class=SensorDeviceClass.POWER,
            unit_of_measurement="W",
        ),
        # ModbusRegisterSensor(
        #     mdb_host.name, mdb_cl,
        #     U64(31397, unit_id, "BatChrg.BatChrg", "Batterieladung"),
        #     device_class=SensorDeviceClass.POWER,
        #     unit_of_measurement="W",
        # ),
        # ModbusRegisterSensor(
        #     mdb_host.name, mdb_cl,
        #     U64(31401, unit_id, "BatDsch.BatDsch", "Batterieentladung"),
        #     device_class=SensorDeviceClass.POWER,
        #     unit_of_measurement="W",
        # ),
    ]

    return sensors
