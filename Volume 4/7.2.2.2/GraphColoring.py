import pycosat
import math
import numpy as np
import pprint as pp
import sys
import collections
from SATUtils import SATUtils


class GraphColoring:
    minOneColor = 1 # (15) Every vertex has at least one color
    adjacentDifColor = 2 # (16) adjacent vertices have different colors


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
        if self.constraints & GraphColoring.adjacentDifColor:
            for vertex in self.nodeDict.keys():
                self.clauses.append([self.NodeToLiteral(vertex, k) for k in range(self.d)])

        # (16) adjacent vertices have different colors
        if self.constraints & GraphColoring.adjacentDifColor:
            for i in [self.NodeToLiteral(x, 0) for x in self.nodeDict]:
                for j in [self.NodeToLiteral(x, 0) for x in self.nodeDict]:
                    if self.literalToIndexTuple(i) in self.nodeDict[self.literalToIndexTuple(j)]:
                        for k in range(self.d):
                            self.clauses.append([-self.NodeToLiteral((self.literalToIndexTuple(i+1)), k),
                                                 -self.NodeToLiteral((self.literalToIndexTuple(j+1)), k)])

