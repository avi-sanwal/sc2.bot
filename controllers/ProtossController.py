from .RaceController import RaceController
from .OffensiveUnit import OffensiveUnit
from sc2.constants import UnitTypeId

class ProtossController(RaceController):

    def __init__(self):
        self.buildQueue = [UnitTypeId.DARKSHRINE, UnitTypeId.FLEETBEACON, 
            UnitTypeId.TEMPLARARCHIVE, UnitTypeId.TWILIGHTCOUNCIL, UnitTypeId.ROBOTICSBAY,
            UnitTypeId.STARGATE, UnitTypeId.ROBOTICSFACILITY, UnitTypeId.CYBERNETICSCORE, UnitTypeId.FORGE]
        self.offenisveUnits = [
            OffensiveUnit(UnitTypeId.ZEALOT, UnitTypeId.GATEWAY, 5),
            OffensiveUnit(UnitTypeId.STALKER, UnitTypeId.GATEWAY),
            OffensiveUnit(UnitTypeId.ADEPT, UnitTypeId.GATEWAY),
            OffensiveUnit(UnitTypeId.SENTRY, UnitTypeId.GATEWAY, 1),
            OffensiveUnit(UnitTypeId.HIGHTEMPLAR, UnitTypeId.GATEWAY),
            OffensiveUnit(UnitTypeId.DARKTEMPLAR, UnitTypeId.GATEWAY),
            OffensiveUnit(UnitTypeId.IMMORTAL, UnitTypeId.ROBOTICSFACILITY),
            OffensiveUnit(UnitTypeId.COLOSSUS, UnitTypeId.ROBOTICSFACILITY),
            OffensiveUnit(UnitTypeId.PHOENIX, UnitTypeId.STARGATE),
            OffensiveUnit(UnitTypeId.VOIDRAY, UnitTypeId.STARGATE),
            OffensiveUnit(UnitTypeId.ORACLE, UnitTypeId.STARGATE),
            OffensiveUnit(UnitTypeId.CARRIER, UnitTypeId.STARGATE),
            OffensiveUnit(UnitTypeId.TEMPEST, UnitTypeId.STARGATE),
            OffensiveUnit(UnitTypeId.MOTHERSHIP, UnitTypeId.NEXUS)]
