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
        self.literalMapping = dict()
        self.reverseLiteralMapping = dict()
        self.auxLiteral = 0
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
        self.StartNodeNeighborConstraints = [[(1, x) for x in startPoints]]
        for startPoint in startPoints:
            self.StartNodeNeighborConstraints.append([(1, x) for x in self.topology[startPoint]] + [(-1, startPoint)])
        self.BaseConstraints += self.StartNodeNeighborConstraints

    def getEndNodeNeighborConstraints(self):
        endPoints = [x[0] for x in self.topology.items() if x[0][0] == 'e']
        self.EndNodeNeighborConstraints = [[(1, x) for x in endPoints]]
        for endPoint in endPoints:
            exactlyOneOf = [self.literalMapping[x] for x in self.topology[endPoint]]
            oneOfClauses = SATUtils.exactlyOne(exactlyOneOf, self.auxLiteral)
            self.auxLiteral = oneOfClauses[1]
            self.clauses
            self.EndNodeNeighborConstraints.append([(1, x) for x in self.topology[endPoint]] + [(-1, endPoint)])
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
        for node in nodeDict.keys():
            self.updateLiteralMapping(node)
        return nodeDict

    def updateLiteralMapping(self, newSymbol):
        if newSymbol not in self.literalMapping:
            self.literalMapping[newSymbol] = self.auxLiteral + 1
            self.reverseLiteralMapping[self.auxLiteral + 1] = newSymbol
            self.auxLiteral += 1

    def getSymbol(self, literal):
        if literal not in self.reverseLiteralMapping:
            if literal <= self.auxLiteral:
                return ('aux', literal)
            else:
                raise Exception('Unknown literal (SAT)')
        else:
            tmp = self.reverseLiteralMapping[literal]
            if literal > 0:
                tmp[0] = 1
            else:
                tmp[0] = -1
            return tmp

    def getLiteral(self, symbol):
        if symbol not in self.literalMapping:
            raise Exception('Unknown symbol (SAT)')
        else:
            if symbol[0] == 'aux':
                return symbol[1]
            tmp = self.reverseLiteralMapping[symbol]
            if symbol > 0:
                tmp[0] = 1
            else:
                tmp[0] = -1
            return tmp
if __name__ == "__main__":
    # main_n = 15
    # main_r = 7
    # allPossible = set([tuple(x[0:main_n]) for x in list(pycosat.itersolve(SATUtils.exactlyR(range(1, main_n+1), main_r)[0]))])
    # pp.pprint(allPossible)
    # print(len(allPossible))
    # print(SATUtils.nCr(main_n, main_r))
    WitnessPuzzle('puzzle2.txt')
