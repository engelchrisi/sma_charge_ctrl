from Register import U32, S32, U64

from modbusreader import ModbusReader


# Holding Register (Halte-Register): Holding Registers sind 16-Bit-Register, die dazu verwendet werden,
# Daten zu speichern oder Parameter in einem Modbus-Gerät zu halten. Diese Register sind schreibbar1
#
# Input Register (Eingangsregister): Im Gegensatz dazu sind Input Registers schreibgeschützt:


def add_sbs37_register(wr: ModbusReader):
    # Input Register:
    wr.add_register(U32(30053, 3, "DevTypeId", "Gerätetyp [RO]"))
    wr.add_register(S32(30775, 3, "PowerAC", "Leistung [RO]"))
    wr.add_register(U32(30783, 3, "GridV1", "Netzspannung Phase L1 [RO]"))
    wr.add_register(S32(30845, 3, "Bat.SOC", "Batterieladezustand in % [RO]"))
    wr.add_register(S32(30865, 3, "TotWIn", "Leistung Bezug [RO]"))
    wr.add_register(S32(30867, 3, "Metering.GridMs.TotWOut", "Leistung Einspeisung [RO]"))
    wr.add_register(U32(31007, 3, "RmgChaTm", "Verbleibende Absorptionszeit der aktuellen Batterieladephase, in s [RO]"))

    wr.add_register(U32(31393, 3, "BatChrg.CurBatCha", "Momentane Batterieladung [RO]"))
    wr.add_register(U32(31395, 3, "BatDsch.CurBatDsch", "Momentane Batterieentladung [RO]"))
    wr.add_register(U64(31397, 3, "BatChrg.BatChrg", "Batterieladung [RO]"))
    wr.add_register(U64(31401, 3, "BatDsch.BatDsch", "Batterieentladung [RO]"))

    # Holding Register:
    wr.add_register(U32(40035, 3, "Batterietyp", "1785 = Lithium-Ionen (Li-Ion) [RO]"))
    wr.add_register(U32(40073, 3, "SelfCsmpBatChaSttMin", "Untere Entladegrenze bei Eigenverbrauchserhöhung, in % [RW]"))  # RW
    wr.add_register(U32(40075, 3, "SelfCsmpBatChaStt", "Eigenverbrauchserhöhung eingeschaltet: 1129 = Ja, 1130 = Nein [RW]"))  # RW
    wr.add_register(U32(40189, 3, "WMaxCha", "Maximale Ladeleistung des Batteriestellers, in W [RO]"))
    wr.add_register(U32(40191, 3, "WMaxDsch", "Maximale Entladeleistung des Batteriestellers, in W [RO]"))
    if False:
        # s. SBS UI => Momentanwerte => "Betriebsstatus der Batterie"
        wr.add_register(S32(40149, 3, "FedInPwrAtCom", "Wirkleistungsvorgabe [WO]"))
        wr.add_register(U32(40151, 3, "FedInSpntCom", "Wirk- und Blindleistungsregelung über Kommunikation [WO]"))
        wr.add_register(U32(40236, 3, "CmpBMSOpMod", "Betriebsart des Batterie-Management-Systems: 303 = Aus, 308 = Ein, 2289 = Batterie laden, 2290 = Batterie entladen, 2424 = Voreinstellung [WO]"))
        wr.add_register(U32(40793, 3, "BatChaMinW", "Minimale Batterieladeleistung, in W [WO]"))
        wr.add_register(U32(40795, 3, "BatChaMaxW", "Maximale Batterieladeleistung, in W [WO]"))
        wr.add_register(U32(40797, 3, "BatDschMinW", "Minimale Batterieentladeleistung, in W [WO]"))
        wr.add_register(U32(40799, 3, "BatDschMaxW", "Maximale Batterieentladeleistung, in W [WO]"))
        wr.add_register(S32(40801, 3, "GridWSpt", "Sollwert der Netzaustauschleistung, in W [WO]"))

    wr.add_register(U32(40647, 3, "AutoUpd", "Automatische Updates eingeschaltet: 1129 = Ja, 1130 = Nein, 1505 = Manuelles Update [RW]"))  # RW


def add_sbs_sunspec_register(wr: ModbusReader):
    # Input Register:
    wr.add_register(U32(40240, 3, "test", "Hesteller [RO]"))
