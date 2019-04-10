import pycosat
import itertools
import math
import numpy as np
import pprint as pp
import sys
import collections
from SATUtils import SATUtils

sign = lambda x: x and (1, -1)[x < 0]

class GraphColoring:
    def  __init__(self, nodeDict, d,
                  minColors=1,# (15) Every vertex has at least one color
                  adjacentDifColor=1 # (16) adjacent vertices have different colors
                  ):
        self.d = d
        self.minColors = minColors
        self.adjacentDifColor = adjacentDifColor
        self.nodeDict = nodeDict
        self.literalToIndexTuple = None
        self.literalToColor = None
        self.nodeToLiteral = None
        self.clauses = []
        self.auxLiteral = -1
        self.origAuxLiteral = -1

    def generateClauses(self):
        if self.auxLiteral == -1:
            raise TypeError()
        #
        # (15) Every vertex has at least minColors color
        for vertex in self.nodeDict.keys():
            literalsToAssertGEKtrue = [self.nodeToLiteral(vertex, k) for k in range(self.d)]
            [subclauses, newHighestLiteral] = SATUtils.atLeast(literalsToAssertGEKtrue ,self.minColors, self.auxLiteral)
            self.auxLiteral = newHighestLiteral + 1
            self.clauses += subclauses

        # (16) adjacent vertices have different colors
        if self.adjacentDifColor != None:
            for i in [self.nodeToLiteral(x, 0) for x in self.nodeDict]:
                for j in [self.nodeToLiteral(x, 0) for x in self.nodeDict]:
                    if self.literalToIndexTuple(i) in self.nodeDict[self.literalToIndexTuple(j)]:
                        for k in range(self.d):
                            self.clauses.append([-self.nodeToLiteral((self.literalToIndexTuple(i)), k),
                                                 -self.nodeToLiteral((self.literalToIndexTuple(j)), k)])

    def viewClauses(self):
        for clause in self.clauses:
            pp.pprint([(sign(literal), self.literalToIndexTuple(abs(literal)), self.literalToColor(abs(literal))) if literal<=self.origAuxLiteral else (sign(literal), 'aux') for literal in clause])

    def defineNodeLiteralConversion(self, literalToIndexTuple, literalToColor, NodeToLiteral):
        for color in range(self.d):
            for testNode in self.nodeDict.keys():
                literal = NodeToLiteral(testNode, color)
                nodeIdentifier = literalToIndexTuple(literal)
                nodeColor = literalToColor(literal)
                if (testNode, color) != (nodeIdentifier, nodeColor):
                    raise TypeError()
                # print((testNode, color))
                # print((nodeIdentifier, nodeColor))
        self.literalToIndexTuple = literalToIndexTuple
        self.literalToColor = literalToColor
        self.nodeToLiteral = NodeToLiteral
        # initialize the auxLiteral to 1 larger than the largest node found during the verification process
        self.auxLiteral = 1 + max([max([abs(self.nodeToLiteral(x, color)) for x in self.nodeDict.keys()]) for color in range(self.d)])
        self.origAuxLiteral = self.auxLiteral

    # given 2 vertices u, v, asserts those 2 vertices differ in at least r colors
    def assertRdiffColors(self, u, v, r):
        [subclauses, newHighestLiteral, cardinalityClauses] = SATUtils.atLeastRsub(\
            [\
                [\
                    [self.nodeToLiteral(u, color), self.nodeToLiteral(v, color)],
                    [-self.nodeToLiteral(u, color), -self.nodeToLiteral(v, color)]\
                ] for color in range(0,self.d)],
                r,
                self.auxLiteral)
        self.auxLiteral = newHighestLiteral + 1
        self.clauses += subclauses

    # returns whether or not u and v share a common neighbor
    def sharesNeighbor(self, u, v):
        # u and v share a neighbor if v is in the neighbor list of any of u's neighbors
        for neighbor in self.nodeDict[u]:
            if neighbor != v and v in self.nodeDict[neighbor]:
                return True
        return False

    # returns whether or not u and v are adjacent
    def isAdjacent(self, u, v):
        return u in self.nodeDict[v]


    @staticmethod
    def generateKClique(nodesInClique):
        nodeDict = dict()
        for i, a in enumerate(nodesInClique):
            for b in nodesInClique[i + 1:]:
                if a != b:
                    if a not in nodeDict:
                        nodeDict[a] = [b]
                    else:
                        nodeDict[a].append(b)
                    if b not in nodeDict:
                        nodeDict[b] = [a]
                    else:
                        nodeDict[b].append(a)
        return nodeDict

    @staticmethod
    def mergeAintoB(adjListA, adjListB):
        for k,v in adjListA.items():
            if k not in adjListB:
                adjListB[k] = v
            else:
                adjListB[k] += v

    @staticmethod
    def merged(adjListA, adjListB):
        bCopy = adjListB.copy()
        GraphColoring.mergeAintoB(adjListA,bCopy)
        return bCopy

    #Path graph
    # A graph where n-2 vertices have exactly 2 neighbors and 2 vertices have 1 neighbor and all vertices are connected
    # AKA a binary tree with only left or only right children
    @staticmethod
    def P(n, zeroIndexed = True):
        if n < 1:
            raise ValueError()
        if n == 1:
            return {0 if zeroIndexed else 1: []}
        nodeDict = dict()
        if zeroIndexed:
            for i in range(0, n):
                if i == 0:
                    nodeDict[0] = (1,)
                elif i == n-1:
                    nodeDict[n-1] = (n-2,)
                else:
                    nodeDict[i] = (i-1, i+1)
        else:
            for i in range(1, n+1):
                if i == 1:
                    nodeDict[1] = (2,)
                elif i == n:
                    nodeDict[n] = (n-1,)
                else:
                    nodeDict[i] = (i-1, i+1)
        return nodeDict

    # Cycle graph
    # A graph where all vertices are part of a single loop of length n
    @staticmethod
    def C(n, zeroIndexed = True):
        if n < 1:
            raise ValueError()
        if n == 1:
            return {0 if zeroIndexed else 1: []}
        nodeDict = dict()
        if zeroIndexed:
            for i in range(0, n):
                    nodeDict[i] = ((i-1) % n, i+1 % n)
        else:
            for i in range(1, n+1):
                    nodeDict[i] = (((i-2) % n)+1, ((i) % n)+1)
        return nodeDict

    # Cycle graph
    # A graph where all vertices connected to all other vertices
    @staticmethod
    def K(n, zeroIndexed = True):
        if n < 1:
            raise ValueError()
        if n == 1:
            return {0 if zeroIndexed else 1: []}
        nodeDict = dict()
        if zeroIndexed:
            for i in range(0, n):
                nodeDict[i] = tuple(list(range(0,i)) + list(range(i+1, n)))
        else:
            for i in range(1, n+1):
                nodeDict[i] = tuple(list(range(1,n+1)[:(i-1)]) + list(range(1, n+1)[i:]))
        return nodeDict

    # disconnects each connected edge and connects each disconnected edge
    @staticmethod
    def invert(nodeDict):
        nodeSet = set(nodeDict.keys())
        newNodeDict = dict()
        for vertex, edges in nodeDict.items():
            newNodeDict[vertex] = tuple(nodeSet.difference(set(list(edges) + [vertex])))
        return newNodeDict

    # https://en.wikipedia.org/wiki/Cartesian_product_of_graphs
    @staticmethod
    def cartesianProduct(G, H):
        vertexSet = itertools.product(G.keys(), H.keys())
        print(list(vertexSet))
        nodeDict = dict()
        for i, vertexA in enumerate(list(itertools.product(G.keys(), H.keys()))[:-1]):
            for vertexB in list(itertools.product(G.keys(), H.keys()))[i:]:
                u=vertexA[0]
                up=vertexA[1]
                v=vertexB[0]
                vp=vertexB[1]
                # distinct vertices (u,u') and (v,v') are adjacent iff:
                # u=v and u' is adjacent to v'
                if u == v and up in H[vp]:
                    if vertexA not in nodeDict:
                        nodeDict[vertexA] = [vertexB]
                    else:
                        nodeDict[vertexA] += [vertexB]
                    if vertexB not in nodeDict:
                        nodeDict[vertexB] = [vertexA]
                    else:
                        nodeDict[vertexB] += [vertexA]
                # u'=v' and u is adjacent to v
                if up == vp and u in G[v]:
                    if vertexA not in nodeDict:
                        nodeDict[vertexA] = [vertexB]
                    else:
                        nodeDict[vertexA] += [vertexB]
                    if vertexB not in nodeDict:
                        nodeDict[vertexB] = [vertexA]
                    else:
                        nodeDict[vertexB] += [vertexA]
        return nodeDict

    # https://en.wikipedia.org/wiki/Lexicographic_product_of_graphs
    @staticmethod
    def lexicographicProduct(G, H, fromScratch=True):
        vertexSet = itertools.product(G.keys(), H.keys())
        print(list(vertexSet))
        nodeDict = dict()
        for i, vertexA in enumerate(list(itertools.product(G.keys(), H.keys()))[:-1]):
            for vertexB in list(itertools.product(G.keys(), H.keys()))[i:]:
                u=vertexA[0]
                up=vertexA[1]
                v=vertexB[0]
                vp=vertexB[1]
                # distinct vertices (u,u') and (v,v') are adjacent iff:
                # u is adjacent to v
                if u in G[v]:
                    if vertexA not in nodeDict:
                        nodeDict[vertexA] = [vertexB]
                    else:
                        nodeDict[vertexA] += [vertexB]
                    if vertexB not in nodeDict:
                        nodeDict[vertexB] = [vertexA]
                    else:
                        nodeDict[vertexB] += [vertexA]
                # u=v and u' is adjacent to v'
                if u == v and up in H[vp]:
                    if vertexA not in nodeDict:
                        nodeDict[vertexA] = [vertexB]
                    else:
                        nodeDict[vertexA] += [vertexB]
                    if vertexB not in nodeDict:
                        nodeDict[vertexB] = [vertexA]
                    else:
                        nodeDict[vertexB] += [vertexA]
        return nodeDict

    # https://en.wikipedia.org/wiki/Strong_product_of_graphs
    @staticmethod
    def strongProduct(G, H, fromScratch=True):
        if fromScratch:
            vertexSet = itertools.product(G.keys(), H.keys())
            print(list(vertexSet))
            nodeDict = dict()
            for i, vertexA in enumerate(list(itertools.product(G.keys(), H.keys()))[:-1]):
                for vertexB in list(itertools.product(G.keys(), H.keys()))[i:]:
                    u=vertexA[0]
                    up=vertexA[1]
                    v=vertexB[0]
                    vp=vertexB[1]
                    # distinct vertices (u,u') and (v,v') are adjacent iff:
                    # u=v and u' is adjacent to v'
                    if u == v and up in H[vp]:
                        if vertexA not in nodeDict:
                            nodeDict[vertexA] = [vertexB]
                        else:
                            nodeDict[vertexA] += [vertexB]
                        if vertexB not in nodeDict:
                            nodeDict[vertexB] = [vertexA]
                        else:
                            nodeDict[vertexB] += [vertexA]
                    # u'=v' and u is adjacent to v
                    if up == vp and u in G[v]:
                        if vertexA not in nodeDict:
                            nodeDict[vertexA] = [vertexB]
                        else:
                            nodeDict[vertexA] += [vertexB]
                        if vertexB not in nodeDict:
                            nodeDict[vertexB] = [vertexA]
                        else:
                            nodeDict[vertexB] += [vertexA]
                    # u is adjacent to v and u' is adjacent to v'
                    if u in G[v] and up in H[vp]:
                        if vertexA not in nodeDict:
                            nodeDict[vertexA] = [vertexB]
                        else:
                            nodeDict[vertexA] += [vertexB]
                        if vertexB not in nodeDict:
                            nodeDict[vertexB] = [vertexA]
                        else:
                            nodeDict[vertexB] += [vertexA]
            return nodeDict
        else:
            return GraphColoring.merged(GraphColoring.cartesianProduct(G,H), GraphColoring.tensorProduct(G,H))

    # https://en.wikipedia.org/wiki/Tensor_product_of_graphs
    @staticmethod
    def tensorProduct(G, H):
        vertexSet = itertools.product(G.keys(), H.keys())
        print(list(vertexSet))
        nodeDict = dict()
        for i, vertexA in enumerate(list(itertools.product(G.keys(), H.keys()))[:-1]):
            for vertexB in list(itertools.product(G.keys(), H.keys()))[i:]:
                u=vertexA[0]
                up=vertexA[1]
                v=vertexB[0]
                vp=vertexB[1]
                # distinct vertices (u,u') and (v,v') are adjacent iff:
                # u is adjacent to v and u' is adjacent to v'
                if u in G[v] and up in H[vp]:
                    if vertexA not in nodeDict:
                        nodeDict[vertexA] = [vertexB]
                    else:
                        nodeDict[vertexA] += [vertexB]
                    if vertexB not in nodeDict:
                        nodeDict[vertexB] = [vertexA]
                    else:
                        nodeDict[vertexB] += [vertexA]
        return nodeDict