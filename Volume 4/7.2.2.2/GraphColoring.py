import pycosat
import itertools
import math
import numpy as np
import pprint as pp
import sys
import collections
from SATUtils import SATUtils, CNF, Clause, Literal, DSAT

sign = lambda x: x and (1, -1)[x < 0]
verboseExpressions = False

class GraphNode:
    def __init__(self, id, color):
        self.ID = id
        self.color = color

class GraphColoring:

    def  __init__(self, nodeDict, d,
                  minColors=1,# (15) Every vertex has at least one color
                  adjacentDifColor=0, # (16) adjacent vertices have different colors
                  maxColors=None #Maximum unique colors per node
                  ):
        self.d = d
        self.minColors = minColors
        self.maxColors = maxColors
        self.adjacentDifColor = adjacentDifColor
        self.nodeDict = nodeDict
        self.literalToIndexTuple = None
        self.literalToColor = None
        self.nodeToLiteral = None
        self.clauses = []
        self.solution = []
        self.auxLiteral = -1
        self.origAuxLiteral = -1
        self.nodeToLiteralDict = dict()
        self.literaToNodeDict = dict()
        self.cnf = CNF()

    def generateClauses(self):
        if self.auxLiteral == -1:
            raise TypeError()
        #
        # (15) Every vertex has at least minColors colors
        if self.minColors != None:
            self.enforceMinColors()

        # Every vertex has at most maxColors colors
        if self.maxColors != None:
            self.enforceMaxColors()

        # (16) adjacent vertices have different colors
        if self.adjacentDifColor != None:
            self.enforceAdjacentDifColor()

    def enforceAdjacentDifColor(self):
        for i in self.nodeDict:
            for j in self.nodeDict:
                if self.isAdjacent(i, j):
                    self.assertNodesDifferInColorByR(i,j,self.adjacentDifColor)

    def enforceMinColors(self):
        for vertex in self.nodeDict.keys():
            literalsToAssertGEKtrue = [self.nodeToLiteral(GraphNode(vertex, k)) for k in range(self.d)]
            [subclauses, newHighestLiteral] = SATUtils.atLeast(literalsToAssertGEKtrue ,self.minColors, self.auxLiteral)
            if verboseExpressions:
                for clause in subclauses:
                    self.cnf.addClause(Clause(clause,
                                              groupComment=str(vertex) + ' has at least ' + str(self.minColors) + ' colors'))
            self.auxLiteral = newHighestLiteral + 1
            self.clauses += subclauses

    def enforceMaxColors(self):
        for vertex in self.nodeDict.keys():
            literalsToAssertLEKtrue = [self.nodeToLiteral(GraphNode(vertex, k)) for k in range(self.d)]
            [subclauses, newHighestLiteral] = SATUtils.atMost(literalsToAssertLEKtrue ,self.minColors, self.auxLiteral)
            if verboseExpressions:
                for clause in subclauses:
                    self.cnf.addClause(Clause(clause,
                                              groupComment=str(vertex) + ' has at most ' + str(self.minColors) + ' colors'))
            self.auxLiteral = newHighestLiteral + 1
            self.clauses += subclauses

    def assertNodesDifferInColorByR(self, nodeA, nodeB, rVal):
        newClauses = []
        #print([-self.nodeToLiteral(GraphNode(nodeA, 0)), -self.nodeToLiteral(GraphNode(nodeB, 0))], [nodeA, nodeB])
        for r in range(rVal):
            for k in range(self.d):
                if k+r < self.d:
                    newClause = [-self.nodeToLiteral(GraphNode(nodeA, k)),
                                         -self.nodeToLiteral(GraphNode(nodeB, k+r))]
                    newClauses.append(newClause)
                    if verboseExpressions:
                        self.cnf.addClause(Clause(newClause,
                                                  comment='not ' + str(k) + ' and ' + str(k+r) + ' at the same time',
                                                  groupComment=str(nodeA) + ' and ' + str(nodeB) +
                                                               ' differ in color by ' + str(rVal)
                                                  ))
                    # make sure to assert the other way too when it's not symmetrical
                    if r != 0:
                        newClause = [-self.nodeToLiteral(GraphNode(nodeA, k+r)),
                                             -self.nodeToLiteral(GraphNode(nodeB, k))]
                        newClauses.append(newClause)
                        if verboseExpressions:
                            self.cnf.addClause(Clause(newClause,
                                                      comment='not ' + str(k+r) + ' and ' + str(k) + ' at the same time',
                                                      groupComment=str(nodeA) + ' and ' + str(nodeB) +
                                                                   ' differ in color by ' + str(rVal)
                                                      ))
        self.clauses += newClauses

    # https://en.wikipedia.org/wiki/L(h,_k)-coloring
    # L(h, k) Coloring
    # L(2, 1) is equivalent to the radio coloring problem
    def L(self, h, k):
        for i in self.nodeDict:
            for j in self.nodeDict:
                if self.nodeToLiteral(GraphNode(i,0)) < self.nodeToLiteral(GraphNode(j,0)):
                    if self.isAdjacent(i, j):
                        self.assertNodesDifferInColorByR(i,j,h)
                    elif self.sharesNeighbor(i, j):
                        self.assertNodesDifferInColorByR(i,j,k)

    def viewClauses(self):
        for clause in self.clauses:
            pp.pprint([(sign(literal), self.literalToIndexTuple(abs(literal)), self.literalToColor(abs(literal))) if literal<=self.origAuxLiteral else (sign(literal), 'aux') for literal in clause])

    def viewSolution(self):
        self.solution = list(pycosat.solve(self.clauses))
        nodeColors = dict()
        if self.solution == list('UNSAT'):
            print(self.solution)
            return False
        for literal in self.solution:
            if literal > 0 and literal<self.origAuxLiteral:
                identifier = self.literalToIndexTuple(literal)
                if identifier not in nodeColors:
                    nodeColors[identifier] = [self.literalToColor(literal)]
                else:
                    nodeColors[identifier].append(self.literalToColor(literal))
        pp.pprint(nodeColors)
        return True
    def viewSolutions(self):
        self.solution = list(pycosat.solve(self.clauses))
        if self.solution == list('UNSAT'):
            print(self.solution)
            return
        for solution in list(pycosat.itersolve(self.clauses)):
            nodeColors = dict()
            for literal in solution:
                if literal > 0 and literal<self.origAuxLiteral:
                    identifier = self.literalToIndexTuple(literal)
                    if identifier not in nodeColors:
                        nodeColors[identifier] = [self.literalToColor(literal)]
                    else:
                        nodeColors[identifier].append(self.literalToColor(literal))
            pp.pprint(nodeColors)

    def defineNodeLiteralConversion(self, literalToID = None, literalToColor = None, GraphNodeToLiteral = None):
        if literalToID == None or literalToColor == None or GraphNodeToLiteral == None:
            self.literaToNodeDict = dict()
            self.nodeToLiteralDict = dict()
            self.auxLiteral = 1
            for node in self.nodeDict.keys():
                self.nodeToLiteralDict[node] = self.auxLiteral
                self.literaToNodeDict[self.auxLiteral] = node
                self.auxLiteral += 1
            literalToID = lambda literal: self.literaToNodeDict[(literal-1)%len(self.nodeDict)+1]
            literalToColor = lambda literal: (literal-1)//len(self.nodeDict)
            GraphNodeToLiteral = lambda gnode: self.nodeToLiteralDict[gnode.ID]+gnode.color*len(self.nodeDict)

        for color in range(self.d):
            for testNode in self.nodeDict.keys():
                literal = GraphNodeToLiteral(GraphNode(testNode, color))
                nodeIdentifier = literalToID(literal)
                nodeColor = literalToColor(literal)
                if (testNode, color) != (nodeIdentifier, nodeColor):
                    raise TypeError()
                # print((testNode, color))
                # print((nodeIdentifier, nodeColor))
        self.literalToIndexTuple = literalToID
        self.literalToColor = literalToColor
        self.nodeToLiteral = GraphNodeToLiteral
        # initialize the auxLiteral to 1 larger than the largest node found during the verification process
        self.auxLiteral = 1 + max([max([abs(self.nodeToLiteral(GraphNode(x, color))) for x in self.nodeDict.keys()]) for color in range(self.d)])
        self.origAuxLiteral = self.auxLiteral

    # given 2 vertices u, v, asserts those 2 vertices differ in at least r colors
    def assertRdiffColors(self, u, v, r):
        groups =[[[self.nodeToLiteral(GraphNode(u, color))], [-self.nodeToLiteral(GraphNode(v, color))]] for color in range(0,self.d)]

        [subclauses, newHighestLiteral, cardinalityClauses] = SATUtils.atLeastRsub( \
                groups,
                r,
                self.auxLiteral)
        self.auxLiteral = newHighestLiteral + 1
        self.clauses += subclauses

        #repeat for positive literals
        groups =[[[-self.nodeToLiteral(GraphNode(u, color))], [self.nodeToLiteral(GraphNode(v, color))]] for color in range(0,self.d)]

        [subclauses, newHighestLiteral, cardinalityClauses] = SATUtils.atLeastRsub(\
                groups,
                r,
                self.auxLiteral)
        self.auxLiteral = newHighestLiteral + 1
        self.clauses += subclauses

    # returns whether or not u and v share a common neighbor
    def sharesNeighbor(self, u, v):
        if u == v: # a node doesn't count as its own neighbor's neighbor
            return False
        # u and v share a neighbor if v is in the neighbor list of any of u's neighbors
        for neighbor in self.nodeDict[u]:
            if self.isAdjacent(v, neighbor):
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

    # Graph corresponding to the United States state border connections
    # https://writeonly.wordpress.com/2009/03/20/adjacency-list-of-states-of-the-united-states-us/
    # which disagrees with http://mathworld.wolfram.com/ContiguousUSAGraph.html
    @staticmethod
    def US(contiguous=False):
        nodeDict = {
            ('AK',): (),\
            ('AL',): (('MS',),('TN',),('GA',),('FL',),),\
            ('AR',): (('MO',),('TN',),('MS',),('LA',),('TX',),('OK',),),\
            ('AZ',): (('CA',),('NV',),('UT',),('NM',),),\
            ('CA',): (('OR',),('NV',),('AZ',),),\
            ('CO',): (('WY',),('NE',),('KS',),('OK',),('NM',),('UT',),),\
            ('CT',): (('NY',),('MA',),('RI',),),\
            ('DC',): (('MD',),('VA',),),\
            ('DE',): (('MD',),('PA',),('NJ',),),\
            ('FL',): (('AL',),('GA',),),\
            ('GA',): (('FL',),('AL',),('TN',),('NC',),('SC',),),\
            ('HI',): (),\
            ('IA',): (('MN',),('WI',),('IL',),('MO',),('NE',),('SD',),),\
            ('ID',): (('MT',),('WY',),('UT',),('NV',),('OR',),('WA',),),\
            ('IL',): (('IN',),('KY',),('MO',),('IA',),('WI',),),\
            ('IN',): (('MI',),('OH',),('KY',),('IL',),),\
            ('KS',): (('NE',),('MO',),('OK',),('CO',),),\
            ('KY',): (('IN',),('OH',),('WV',),('VA',),('TN',),('MO',),('IL',),),\
            ('LA',): (('TX',),('AR',),('MS',),),\
            ('MA',): (('RI',),('CT',),('NY',),('NH',),('VT',),),\
            ('MD',): (('VA',),('WV',),('PA',),('DC',),('DE',),),\
            ('ME',): (('NH',),),\
            ('MI',): (('WI',),('IN',),('OH',),),\
            ('MN',): (('WI',),('IA',),('SD',),('ND',),),\
            ('MO',): (('IA',),('IL',),('KY',),('TN',),('AR',),('OK',),('KS',),('NE',),),\
            ('MS',): (('LA',),('AR',),('TN',),('AL',),),\
            ('MT',): (('ND',),('SD',),('WY',),('ID',),),\
            ('NC',): (('VA',),('TN',),('GA',),('SC',),),\
            ('ND',): (('MN',),('SD',),('MT',),),\
            ('NE',): (('SD',),('IA',),('MO',),('KS',),('CO',),('WY',),),\
            ('NH',): (('VT',),('ME',),('MA',),),\
            ('NJ',): (('DE',),('PA',),('NY',),),\
            ('NM',): (('AZ',),('CO',),('OK',),('TX',),),\
            ('NV',): (('ID',),('UT',),('AZ',),('CA',),('OR',),),\
            ('NY',): (('NJ',),('PA',),('VT',),('MA',),('CT',),),\
            ('OH',): (('PA',),('WV',),('KY',),('IN',),('MI',),),\
            ('OK',): (('KS',),('MO',),('AR',),('TX',),('NM',),('CO',),),\
            ('OR',): (('CA',),('NV',),('ID',),('WA',),),\
            ('PA',): (('NY',),('NJ',),('DE',),('MD',),('WV',),('OH',),),\
            ('RI',): (('CT',),('MA',),),\
            ('SC',): (('GA',),('NC',),),\
            ('SD',): (('ND',),('MN',),('IA',),('NE',),('WY',),('MT',),),\
            ('TN',): (('KY',),('VA',),('NC',),('GA',),('AL',),('MS',),('AR',),('MO',),),\
            ('TX',): (('NM',),('OK',),('AR',),('LA',),),\
            ('UT',): (('ID',),('WY',),('CO',),('AZ',),('NV',),),\
            ('VA',): (('NC',),('TN',),('KY',),('WV',),('MD',),('DC',),),\
            ('VT',): (('NY',),('NH',),('MA',),),\
            ('WA',): (('ID',),('OR',),),\
            ('WI',): (('MI',),('MN',),('IA',),('IL',),),\
            ('WV',): (('OH',),('PA',),('MD',),('VA',),('KY',),),\
            ('WY',): (('MT',),('SD',),('NE',),('CO',),('UT',),('ID',),)\
        }
        if contiguous:
            del nodeDict[('AK',)]
            del nodeDict[('HI',)]
        return nodeDict