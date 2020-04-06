import pprint as pp
from SortUtils import SortUtils
import math
import abc

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

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

    # Add element
    @abc.abstractmethod
    def AddPair(self, element, hashedElement):
        pass

    # Return element or None if it doesn't exist
    @abc.abstractmethod
    def GetPair(self, element, hashedElement):
        pass

    # Remove element
    @abc.abstractmethod
    def RemovePair(self, element, hashedElement):
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

    def Remove(self, element):
        return self.RemovePair(element, self.H(element))

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

    # Add element
    def AddPair(self, element, hashedElement):
        self.HashStructure[hashedElement] = element

    # Return element or None if it doesn't exist
    def GetPair(self, element, hashedElement):
        return self.HashStructure[hashedElement]

    # Remove element
    def RemovePair(self, element, hashedElement):
        if self.HashStructure[hashedElement] == element:
            self.HashStructure[hashedElement] = None

class FailOnCollision(CollisionBase):
    # Set up the data structure needed to do hashing
    def SetupCollision(self, initInfo):
        self.capacity = initInfo['M']
        self.HashStructure = [None] * self.capacity

    # Add element to HashMap
    def AddPair(self, element, hashedElement):
        if self.HashStructure[hashedElement] is not None:
            raise Exception('Collision!')
        self.HashStructure[hashedElement] = element

    # Return element or None if it doesn't exist
    def GetPair(self, element, hashedElement):
        return self.HashStructure[hashedElement]

    # Remove element
    def RemovePair(self, element, hashedElement):
        if self.HashStructure[hashedElement] == element:
            self.HashStructure[hashedElement] = None

class LinearListCollision(CollisionBase):
    # Set up the data structure needed to do hashing
    def SetupCollision(self, initInfo):
        self.capacity = initInfo['M']
        self.HashStructure = [None] * self.capacity

    # Add element
    def AddPair(self, element, hashedElement):
        if self.HashStructure[hashedElement] == None:
            self.HashStructure[hashedElement] = Node(element)
        else:
            newStart = Node(element)
            newStart.next = self.HashStructure[hashedElement]
            self.HashStructure[hashedElement] = newStart

    # Return element or None if it doesn't exist
    def GetPair(self, element, hashedElement):
        if self.HashStructure[hashedElement] is None:
            return None
        curr = self.HashStructure[hashedElement]
        while curr is not None:
            if curr.data == element:
                return element
            curr = curr.next
        return None


    # Remove element
    def RemovePair(self, element, hashedElement):
        if self.HashStructure[hashedElement] is not None:
            curr = self.HashStructure[hashedElement]
            last = None
            while curr is not None:
                if curr.data == element:
                    # found the element
                    if last is not None:
                        last.next = curr.next
                    else:
                        self.HashStructure[hashedElement] = curr.next
                last = curr
                curr = curr.next

class CompareHashing:
    def __init__(self, algoA, algoB):
        self.algoA = algoA
        self.algoB = algoB

if __name__ == '__main__':
    HB = HashBase.GenAlgorithm(OverwriteOnCollision, ModuloHashFunc)
    HB.Initialize([1, 4, 14, 24, 7, 17, 27, 3, 13, 23], {'M': 10})
    HB.Remove(4)
    HB.Remove(17)
    HB.Remove(23)
    print(HB.HashStructure)