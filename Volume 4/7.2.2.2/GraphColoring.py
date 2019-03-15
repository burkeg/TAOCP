import pycosat
import math
import numpy as np
import pprint as pp
import sys
import collections
from SATUtils import SATUtils


class GraphColoring:
    # list of different constraints to apply on the graph that don't depend
    # repeatedly testing solutions (such as maximizing regions with 2 colors)
    constraint_minOneColor = 1         # (15) Every vertex has at least one color
    constraint_adjacentDifColor = 2    # (16) adjacent vertices have different colors


    def  __init__(self, nodeDict, d):
        self.d = d
        self.nodeDict = nodeDict
        self.literalToIndexTuple = None
        self.literalToColor = None
        self.NodeToLiteral = None
        self.constraints = 0
        self.clauses = []

    def generateClauses(self):
        # (15) Every vertex has at least one color
        if self.constraints & GraphColoring.constraint_adjacentDifColor:
            for vertex in self.nodeDict.keys():
                self.clauses.append([self.NodeToLiteral(vertex, k) for k in range(self.d)])

        # (16) adjacent vertices have different colors
        if self.constraints & GraphColoring.constraint_adjacentDifColor:
            for i in [self.NodeToLiteral(x, 0) for x in self.nodeDict]:
                for j in [self.NodeToLiteral(x, 0) for x in self.nodeDict]:
                    if self.literalToIndexTuple(i) in self.nodeDict[self.literalToIndexTuple(j)]:
                        for k in range(self.d):
                            self.clauses.append([-self.NodeToLiteral((self.literalToIndexTuple(i+1)), k),
                                                 -self.NodeToLiteral((self.literalToIndexTuple(j+1)), k)])

    def defineNodeLiteralConversion(self, literalToIndexTuple, literalToColor, NodeToLiteral):
        # test to make sure some literal actually work
        for testLiteral in range(1,10):
            # print('testLiteral', testLiteral)
            # print('literalToIndexTuple', literalToIndexTuple(testLiteral))
            # print('literalToColor',literalToColor(testLiteral))
            # print('NodeToLiteral', NodeToLiteral(literalToIndexTuple(testLiteral), literalToColor(testLiteral)))
            if NodeToLiteral(literalToIndexTuple(testLiteral), literalToColor(testLiteral)) != testLiteral:
                raise TypeError()
            else:
                self.literalToIndexTuple = literalToIndexTuple
                self.literalToColor = literalToColor
                self.NodeToLiteral = NodeToLiteral
