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
        self.auxLiteral = 1
        self.intepretPuzzle()
        self.Vn = [] # Set of all normal nodes
        self.Vs = [] # Set of all start nodes
        self.Ve = [] # Set of all end nodes

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
        self.Vn = [x for x in self.topology if isinstance(x[0], int) and isinstance(x[1], int)]
        self.Vs = [x for x in self.topology if 's' == x[0]]
        self.Ve = [x for x in self.topology if 'e' == x[0]]

        # Filter out the symbol dict so only special rules are left
        del symbolDict['s']
        del symbolDict['|']
        del symbolDict['+']
        del symbolDict['-']
        del symbolDict['e']
        # pp.pprint(self.topology)
        # pp.pprint(symbolDict)
        self.symbolDict = symbolDict

        self.getConstraints()
        # pp.pprint(self.NormalNodeNeighborConstraints)
        # pp.pprint(self.StartNodeNeighborConstraints)
        # pp.pprint(self.EndNodeNeighborConstraints)
        pp.pprint([y for y in [self.getSymbol(x) for x in pycosat.solve(self.clauses)] if y[1][0] != 'aux'])
        # pp.pprint(pycosat.solve(self.clauses))

    def getConstraints(self):
        self.getBaseConstraints()

    def getBaseConstraints(self):
        self.getNormalNodeNeighborConstraints()
        self.getStartNodeNeighborConstraints()
        self.getEndNodeNeighborConstraints()
        self.getHexagonalconstraints()

    def getHexagonalconstraints(self):
        for hex in self.symbolDict['hexagon']:
            self.clauses.append([self.getLiteral((1, hex[0]))])

    def getNormalNodeNeighborConstraints(self):
        normalPoints = self.Vn
        for normalPoint in normalPoints:
            # Assert exactly 2 neighbors to a normal point are ever true
            twoOfClauses = SATUtils.exactlyR([self.getLiteral((1, x)) for x in self.topology[normalPoint]], 2, self.auxLiteral)
            self.auxLiteral = twoOfClauses[1] + 1 if twoOfClauses[1] >= self.auxLiteral else self.auxLiteral

            # Only enforce the previous condition when the normal point is being used
            self.NormalNodeNeighborConstraints += [x + [self.getLiteral((-1, normalPoint))] for x in twoOfClauses[0]]
        self.clauses += self.NormalNodeNeighborConstraints
        self.NormalNodeNeighborConstraints = [[self.getSymbol(literal) for literal in clause] for clause in self.NormalNodeNeighborConstraints]
        self.BaseConstraints += self.NormalNodeNeighborConstraints

    def getStartNodeNeighborConstraints(self):
        startPoints = self.Vs
        # assert at least 1 start point is true
        self.StartNodeNeighborConstraints = [[self.getLiteral((1, x)) for x in startPoints]]
        for startPoint in startPoints:
            # Assert exactly one neighbor to a startpoint is ever true
            oneOfClauses = SATUtils.exactlyOne([self.getLiteral((1, x)) for x in self.topology[startPoint]], self.auxLiteral)
            self.auxLiteral = oneOfClauses[1] + 1 if oneOfClauses[1] >= self.auxLiteral else self.auxLiteral

            # Only enforce the previous condition when the startpoint is being used
            self.StartNodeNeighborConstraints += [x + [self.getLiteral((-1, startPoint))] for x in oneOfClauses[0]]
        self.clauses += self.StartNodeNeighborConstraints
        self.StartNodeNeighborConstraints = [[self.getSymbol(literal) for literal in clause] for clause in self.StartNodeNeighborConstraints]
        self.BaseConstraints += self.StartNodeNeighborConstraints

    def getEndNodeNeighborConstraints(self):
        endPoints = self.Ve
        # assert at least 1 end point is true
        self.EndNodeNeighborConstraints = [[self.getLiteral((1, x)) for x in endPoints]]
        for endPoint in endPoints:
            # Assert exactly one neighbor to an endpoint is ever true
            oneOfClauses = SATUtils.exactlyOne([self.getLiteral((1, x)) for x in self.topology[endPoint]], self.auxLiteral)
            self.auxLiteral = oneOfClauses[1] + 1 if oneOfClauses[1] >= self.auxLiteral else self.auxLiteral

            # Only enforce the previous condition when the endpoint is being used
            self.EndNodeNeighborConstraints += [x + [self.getLiteral((-1, endPoint))] for x in oneOfClauses[0]]
        self.clauses += self.EndNodeNeighborConstraints
        self.EndNodeNeighborConstraints = [[self.getSymbol(literal) for literal in clause] for clause in self.EndNodeNeighborConstraints]
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
            self.literalMapping[newSymbol] = self.auxLiteral
            self.reverseLiteralMapping[self.auxLiteral] = newSymbol
            self.auxLiteral += 1

    def getSymbol(self, literal):
        if abs(literal) not in self.reverseLiteralMapping:
            if abs(literal) <= self.auxLiteral:
                return (1 if literal > 0 else -1, ('aux', literal))
            else:
                raise Exception('Unknown literal (SAT)')
        else:
            tmp = self.reverseLiteralMapping[abs(literal)]
            if literal > 0:
                return (1, tmp)
            else:
                return (-1, tmp)

    def getLiteral(self, symbol):
        polarity = symbol[0]
        name = symbol[1][0]
        auxLiteral = symbol[1][1]
        if symbol[1] not in self.literalMapping:
            raise Exception('Unknown symbol (SAT)')
        else:
            if name == 'aux':
                return auxLiteral*polarity
            tmp = self.literalMapping[symbol[1]]
            return tmp*polarity

if __name__ == "__main__":
    # main_n = 15
    # main_r = 7
    # allPossible = set([tuple(x[0:main_n]) for x in list(pycosat.itersolve(SATUtils.exactlyR(range(1, main_n+1), main_r)[0]))])
    # pp.pprint(allPossible)
    # print(len(allPossible))
    # print(SATUtils.nCr(main_n, main_r))
    WitnessPuzzle('puzzle2.txt')
