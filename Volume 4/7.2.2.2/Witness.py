import pycosat
import math
import numpy as np
import pprint as pp
import sys
import collections
import re
from SATUtils import SATUtils
from collections import namedtuple
from GraphColoring import GraphColoring

class WitnessPuzzle:
    def  __init__(self, fname):
        self.fname = fname
        self.NormalNodeNeighborConstraints = []
        self.StartNodeNeighborConstraints = []
        self.EndNodeNeighborConstraints = []
        self.BaseConstraints = []
        self.intepretPuzzle()

    def intepretPuzzle(self):
        puzzleFile = []
        gridDimensions = []
        symbolDict = dict()
        self.clauses = []
        with open(self.fname) as f:
            puzzleFile = f.readlines()
        for i, line in enumerate([x.strip('\n') for x in puzzleFile]):
            # First line, tells the dimensions of the puzzle
            if i == 0:
                gridDimensions = [int(x) for x in line.split(',')]
                continue

            # Read in the puzzle topology
            if i >= 2 and i < 2 + gridDimensions[0]:
                row = i - 2
                col = 0
                for symbol in line:
                    if symbol == ' ':
                        col = col + 1
                        continue
                    if symbol not in symbolDict:
                        symbolDict[symbol] = [(row, col)]
                    else:
                        symbolDict[symbol].append((row, col))
                    col = col + 1
                continue

            # Read in additional puzzle symbols
            if i > 2 + gridDimensions[0]:
                fields = [x.strip(' ') for x in line.split(',')]

                # hexagon constraints
                # (coordinate, color)
                # coordinate = (i, j)
                # i = row position (0-indexed)
                # j = column position (0-indexed)
                # color = integer representing color
                if fields[0] == 'hexagon':
                    if fields[0] not in symbolDict:
                        symbolDict[fields[0]] = [((int(fields[1]), int(fields[2])), int(fields[3]))]
                    else:
                        symbolDict[fields[0]].append(((int(fields[1]), int(fields[2])), int(fields[3])))
                continue

        # Get the topology of the puzzle
        self.topology =  self.generatePuzzleTopology(symbolDict)

        # Filter out the symbol dict so only special rules are left
        del symbolDict['s']
        del symbolDict['|']
        del symbolDict['+']
        del symbolDict['-']
        del symbolDict['e']
        pp.pprint(self.topology)
        pp.pprint(symbolDict)

        self.getConstraints()
        pp.pprint(self.StartNodeNeighborConstraints)
        pp.pprint(self.EndNodeNeighborConstraints)

    def getConstraints(self):
        self.getBaseConstraints()

    def getBaseConstraints(self):
        self.getNormalNodeNeighborConstraints()
        self.getStartNodeNeighborConstraints()
        self.getEndNodeNeighborConstraints()

    def getNormalNodeNeighborConstraints(self):
        pass

    def getStartNodeNeighborConstraints(self):
        startPoints = [x[0] for x in self.topology.items() if x[0][0] == 's']
        self.StartNodeNeighborConstraints = [[(True, x) for x in startPoints]]
        for startPoint in startPoints:
            self.StartNodeNeighborConstraints.append([(True, x) for x in self.topology[startPoint]] + [(False, startPoint)])
        self.BaseConstraints += self.StartNodeNeighborConstraints

    def getEndNodeNeighborConstraints(self):
        endPoints = [x[0] for x in self.topology.items() if x[0][0] == 'e']
        self.EndNodeNeighborConstraints = [[(True, x) for x in endPoints]]
        for endPoint in endPoints:
            self.EndNodeNeighborConstraints.append([(True, x) for x in self.topology[endPoint]] + [(False, endPoint)])
        self.BaseConstraints += self.EndNodeNeighborConstraints

    def generatePuzzleTopology(self, symbolDict):
        nodeDict = dict()

        # At each junction in the puzzle, make sure all surrounding edges form a k-clique
        for junction in symbolDict['+']:
            nodesInClique = [x for x in symbolDict['-'] + symbolDict['|'] \
                             if (abs(x[0]-junction[0]) == 1 and abs(x[1]-junction[1]) == 0) \
                             or (abs(x[0]-junction[0]) == 0 and abs(x[1]-junction[1]) == 1)]
            for i, a in enumerate(nodesInClique):
                for b in nodesInClique[i+1:]:
                    if a != b:
                        if a not in nodeDict:
                            nodeDict[a] = [b]
                        else:
                            nodeDict[a].append(b)
                        if b not in nodeDict:
                            nodeDict[b] = [a]
                        else:
                            nodeDict[b].append(a)

        # At each start in the puzzle, make sure all surrounding edges form a k-clique
        for junction in symbolDict['s']:
            nodesInClique = [x for x in symbolDict['-'] + symbolDict['|'] \
                             if (abs(x[0]-junction[0]) == 1 and abs(x[1]-junction[1]) == 0) \
                             or (abs(x[0]-junction[0]) == 0 and abs(x[1]-junction[1]) == 1)]
            nodesInClique += [('s', junction[0], junction[1])]
            cliqueDict = GraphColoring.generateKClique(nodesInClique)
            GraphColoring.mergeAintoB(cliqueDict, nodeDict)

        # At each end in the puzzle, make sure all surrounding edges form a k-clique
        for junction in symbolDict['e']:
            nodesInClique = [x for x in symbolDict['-'] + symbolDict['|'] \
                             if (abs(x[0]-junction[0]) == 1 and abs(x[1]-junction[1]) == 0) \
                             or (abs(x[0]-junction[0]) == 0 and abs(x[1]-junction[1]) == 1)]
            nodesInClique += [('e', junction[0], junction[1])]
            cliqueDict = GraphColoring.generateKClique(nodesInClique)
            GraphColoring.mergeAintoB(cliqueDict, nodeDict)
        return nodeDict


if __name__ == "__main__":
    # main_n = 15
    # main_r = 7
    # allPossible = set([tuple(x[0:main_n]) for x in list(pycosat.itersolve(SATUtils.exactlyR(range(1, main_n+1), main_r)[0]))])
    # pp.pprint(allPossible)
    # print(len(allPossible))
    # print(SATUtils.nCr(main_n, main_r))
    WitnessPuzzle('puzzle2.txt')
