import matplotlib.pyplot as plt
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import sc2
from sc2.position import Point2
from sc2.constants import UnitTypeId

class PositionObstructionCalculator:

    def __init__(self, botAI: sc2.BotAI):
        self.botAI = botAI

    def doesPositionObstructWorkers(self, p: Point2):
        townhalls = self.botAI.units.of_type([UnitTypeId.NEXUS, UnitTypeId.COMMANDCENTER, UnitTypeId.HATCHERY])
        if not townhalls:
            return True
        townhall = townhalls.closest_to(p)
        mineralFields = self.botAI.state.units.of_type([UnitTypeId.MINERALFIELD, UnitTypeId.MINERALFIELD450, UnitTypeId.MINERALFIELD750]).closer_than(self.botAI.EXPANSION_GAP_THRESHOLD, townhall)
        vespene_geysers = self.botAI.state.units.vespene_geyser.closer_than(self.botAI.EXPANSION_GAP_THRESHOLD, townhall)
        points = [townhall.position.to2]
        points.extend([geyser.position.to2 for geyser in vespene_geysers])
        points.extend([field.position.to2 for field in mineralFields])
        points = self._GiftWrapping(points)
        return Polygon(points).contains(Point(p.x + 1, p.y + 1)) or Polygon(points).contains(Point(p.x - 1, p.y - 1)) \
         or Polygon(points).contains(Point(p.x + 1, p.y - 1)) or Polygon(points).contains(Point(p.x - 1, p.y + 1))

    def _CCW(self, p1, p2, p3):
        if (p3[1]-p1[1])*(p2[0]-p1[0]) >= (p2[1]-p1[1])*(p3[0]-p1[0]):
            return True
        return False

    def _GiftWrapping(self, S):
        n = len(S)
        P = [None] * n
        pointOnHull = min(S, key = lambda t: t[0])
        i = 0
        while True:
            P[i] = pointOnHull
            endpoint = S[0]
            for j in range(1,n):
                if (endpoint[0] == pointOnHull[0] and endpoint[1] == pointOnHull[1]) or not self._CCW(S[j],P[i],endpoint):
                    endpoint = S[j]
            i = i + 1
            pointOnHull = endpoint
            if endpoint[0] == P[0][0] and endpoint[1] == P[0][1]:
                break
        for i in range(n):
            if P[-1] == None:
                del P[-1]
        return P
