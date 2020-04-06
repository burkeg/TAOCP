import pprint as pp
from SortUtils import SortUtils
import math
import abc

class HashFuncBase(metaclass=abc.ABCMeta):
    # Set up the data structure needed to do hashing
    @abc.abstractmethod
    def SetupHashFunc(self, initInfo):
        pass

    # Hashes the data in the format
    @abc.abstractmethod
    def H(self, data):
        pass

class CollisionBase(metaclass=abc.ABCMeta):
    def __init__(self):
        self.HashStructure = None

    # Set up the data structure needed to do hashing
    @abc.abstractmethod
    def SetupCollision(self, initInfo):
        pass

    # Add element to HashMap
    @abc.abstractmethod
    def AddPair(self, element, hashedElement):
        pass

    # return element in HashMap or None if it doesn't exist
    @abc.abstractmethod
    def GetPair(self, element, hashedElement):
        pass

class HashBase(HashFuncBase, CollisionBase):
    @staticmethod
    def GenAlgorithm(CollisionPolicy, HashFuncPolicy):
        return (type(CollisionPolicy.__name__ + '_' + HashFuncPolicy.__name__, (CollisionPolicy, HashFuncPolicy, HashBase), {}))()

    def Initialize(self, incomingData=None, initInfo=None):
        if incomingData is None:
            incomingData = []
        if initInfo is None:
            initInfo = dict()
        self.SetupCollision(initInfo)
        self.SetupHashFunc(initInfo)
        for element in incomingData:
            self.Add(element)

    def Add(self, element):
        self.AddPair(element, self.H(element))

    def Get(self, element):
        return self.GetPair(element, self.H(element))

class ModuloHashFunc(HashFuncBase):
    def __init__(self):
        self.modulo = None

    # Set up the data structure needed to do hashing
    def SetupHashFunc(self, initInfo):
        self.modulo = initInfo['M']

    def H(self, data):
        return data % self.modulo

class OverwriteOnCollision(CollisionBase):
    # Set up the data structure needed to do hashing
    def SetupCollision(self, initInfo):
        self.capacity = initInfo['M']
        self.HashStructure = [None] * self.capacity

    # Add element to HashMap
    def AddPair(self, element, hashedElement):
        self.HashStructure[hashedElement] = element

    # return element in HashMap or None if it doesn't exist
    def GetPair(self, element, hashedElement):
        return self.HashStructure[hashedElement]


if __name__ == '__main__':
    # HB = OverwriteModuloHash()
    HB = HashBase.GenAlgorithm(OverwriteOnCollision, ModuloHashFunc)
    HB.Initialize([1, 4, 14, 17], {'M': 10})
    print(HB.HashStructure)