from sc2.constants import UnitTypeId

class OffensiveUnit:

    type = None
    trainedFrom = None
    probabilityToTrain = 0.1
    maxTrainCount = 20

    def __init__(self, type: UnitTypeId, trainedFrom: UnitTypeId, maxTrainCount: int=20):
        self.type = type
        self.trainedFrom = trainedFrom
        self.maxTrainCount = maxTrainCount
