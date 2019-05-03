import random
import asyncio
import sc2
from sc2 import run_game, maps, Race, Difficulty, ActionResult
from sc2.player import Bot, Computer
from sc2.units import Units, Unit
from sc2.constants import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
from typing import Union, Optional
from controllers.ProtossController import ProtossController
from placement.PositionObstructionCalculator import PositionObstructionCalculator

class SentBot(sc2.BotAI):

    EXPANSION_GAP_THRESHOLD = 20

    def on_start(self):
        self.townhall_type = {Race.Protoss: UnitTypeId.NEXUS,
                              Race.Terran: UnitTypeId.COMMANDCENTER, Race.Zerg: UnitTypeId.HATCHERY}[self.race]
        self.worker_type = {Race.Protoss: UnitTypeId.PROBE,
                            Race.Terran: UnitTypeId.SCV, Race.Zerg: UnitTypeId.DRONE}[self.race]
        self.supply_type = {Race.Protoss: UnitTypeId.PYLON,
                            Race.Terran: UnitTypeId.SUPPLYDEPOT, Race.Zerg: UnitTypeId.OVERLORD}[self.race]
        self.gas_collector_type = {Race.Protoss: UnitTypeId.ASSIMILATOR,
                                   Race.Terran: UnitTypeId.REFINERY, Race.Zerg: UnitTypeId.EXTRACTOR}[self.race]
        self.barracks_type = {Race.Protoss: UnitTypeId.GATEWAY,
                                   Race.Terran: UnitTypeId.BARRACKS, Race.Zerg: UnitTypeId.HATCHERY}[self.race]
        self.tower_type = {Race.Protoss: UnitTypeId.PHOTONCANNON,
                                   Race.Terran: UnitTypeId.BUNKER, Race.Zerg: UnitTypeId.SPINECRAWLER}[self.race]
        self.mainBase = None
        self.controller = ProtossController()
        self.positionObstructionCalculator = PositionObstructionCalculator(self)

    async def on_step(self, iteration):
        if self.units(self.townhall_type).amount < 4 and self.can_afford(self.townhall_type) and not self.already_pending(self.townhall_type):
            await self.expand_now()
            return
        
        if not self.mainBase:
            if self.units(self.townhall_type).amount < 1:
                return
            self.mainBase = self.units(self.townhall_type).first

        for townhall in self.units(self.townhall_type).ready:
            worker_count = (self.state.units.of_type([UnitTypeId.MINERALFIELD, UnitTypeId.MINERALFIELD450, UnitTypeId.MINERALFIELD750]). \
                closer_than(10, townhall).filter(lambda unit: unit.mineral_contents > 0).amount * 2) + (self.state.units.of_type(UnitTypeId.VESPENEGEYSER). \
                closer_than(10, townhall).filter(lambda unit: unit.has_vespene).amount * 3)
            await self.train_unit(fromBuilding=self.townhall_type, unitType=self.worker_type, max_count=worker_count)
            await self.ensure_base_buildings(self.supply_type, townhall, 6)
            if self.state.units.of_type(self.supply_type).closer_than(self.EXPANSION_GAP_THRESHOLD, townhall).ready.amount > 0:
                await self.build_gas_collector(townhall)
                await self.ensure_base_buildings(self.barracks_type, townhall, 1)
                await self.ensure_base_buildings(self.tower_type, townhall, 4)
                if self.minerals > 400 or len(self.controller.buildQueue) <= 0:
                    await self.train_army(townhall)

        if self.minerals > 400:
            await self.build_single_buildings()
        await self.distribute_workers()
        await self.check_and_attack(8)
        await asyncio.sleep((random.random() * 0.1 + 0.01))

    async def build_gas_collector(self, townhall):
        vespene_geysers = self.state.units.vespene_geyser.closer_than(self.EXPANSION_GAP_THRESHOLD, townhall).filter(lambda unit:
                len(self.units.closer_than(10, unit).of_type(self.gas_collector_type)) == 0)
        for geyser in vespene_geysers:
            unit = self.select_build_worker(geyser)
            if unit and self.can_afford(self.gas_collector_type):
                return await self.do(unit.build(self.gas_collector_type, geyser))

    async def build_single_buildings(self):
        if len(self.controller.buildQueue) < 1:
            return
        head = self.controller.buildQueue.pop()
        result = await self.ensure_base_buildings(building=head, nearUnit=self.mainBase, max_count=1)
        if result != ActionResult.Success:
            self.controller.buildQueue.append(head)

    async def ensure_base_buildings(self, building: UnitTypeId, nearUnit: Unit, max_count: int=1):
        if building == UnitTypeId.NOTAUNIT:
            return ActionResult.Error
        if self.units(building).closer_than(self.EXPANSION_GAP_THRESHOLD, nearUnit).amount >= max_count:
            return ActionResult.Success
        if not self.already_pending(building) and self.can_afford(building):
            p = await self.find_placement(building, nearUnit.position.to2, max_distance=self.EXPANSION_GAP_THRESHOLD)
            if (not p):
                print("No viable placement found for", building)
                return ActionResult.CantFindPlacementLocation
            if (self.positionObstructionCalculator.doesPositionObstructWorkers(p)):
                print(p, "obstructs workers", "skipping")
                return ActionResult.CantFindPlacementLocation
            return await self.build(building, p)
        return ActionResult.Error

    async def train_unit(self, fromBuilding: UnitTypeId, unitType: UnitTypeId, max_count: int=2):
        buildings = self.units(fromBuilding).ready.noqueue
        if not buildings:
            return
        existingUnitCount = self.units.of_type(unitType).closer_than(self.EXPANSION_GAP_THRESHOLD, buildings.random).amount
        if existingUnitCount >= max_count:
            return
        for building in buildings:
            if self.can_afford(unitType):
                await self.do(building.train(unitType))
    
    async def check_and_attack(self, strength: int):
        """attackUnits = self.units.not_structure.filter(lambda unit: unit.can_attack and not 
            (unit.type_id in (UnitTypeId.PROBE, UnitTypeId.SCV, UnitTypeId.DRONE) or unit.is_moving or unit.is_attacking))
        if len(attackUnits) < strength:
            return
        await self.chat_send("Sending %d units for attack" % len(attackUnits))
        for unit in attackUnits:
            await self.do(unit.attack(self.enemy_start_locations.random))"""

    async def train_army(self, townhall: Unit):
        unitToTrain = random.choice(self.controller.offenisveUnits)
        barracks = self.units(unitToTrain.trainedFrom).closer_than(self.EXPANSION_GAP_THRESHOLD, townhall).ready.noqueue
        if not barracks:
            return
        if self.can_afford(unitToTrain.type) and self.units(unitToTrain.type).amount < unitToTrain.maxTrainCount:
            await self.do(barracks.random.train(unitToTrain.type))

    async def find_placement(self, building: UnitTypeId, near: Union[Unit, Point2, Point3], max_distance: int=20, random_alternative: bool=True, placement_step: int=2) -> Optional[Point2]:
        """Finds a placement location for building."""

        assert isinstance(building, (AbilityId, UnitTypeId))
        assert isinstance(near, Point2)

        if isinstance(building, UnitTypeId):
            building = self._game_data.units[building.value].creation_ability
        else:  # AbilityId
            building = self._game_data.abilities[building.value]

        if await self.can_place(building, near):
            return near

        if max_distance == 0:
            return None

        for distance in range(placement_step, max_distance, placement_step):
            possible_positions = [Point2(p).offset(near).to2 for p in (
                    [(dx, -distance) for dx in range(-distance, distance + 1, placement_step)] +
                    [(dx, distance) for dx in range(-distance, distance + 1, placement_step)] +
                    [(-distance, dy) for dy in range(-distance, distance + 1, placement_step)] +
                    [(distance, dy) for dy in range(-distance, distance + 1, placement_step)]
            )]
            res = await self._client.query_building_placement(building, possible_positions)
            possible = [p for r, p in zip(res, possible_positions) if r == ActionResult.Success and not self.positionObstructionCalculator.doesPositionObstructWorkers(p)]
            if not possible:
                continue

            if random_alternative:
                return random.choice(possible)
            else:
                return min(possible, key=lambda p: p.distance_to(near))
        return None

run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, SentBot()),
    Computer(Race.Protoss, Difficulty.Medium)
], realtime=True)
