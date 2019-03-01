import pycosat
import math
import numpy as np
import pprint as pp
import sys
import collections
from SATUtils import SATUtils

class McGregor:
    def  __init__(self, n, d, variant='default', all=False):
        if (n < 3):
            raise ValueError()
        self.variant = variant
        self.n = n
        self.doAll = all
        self.d = d
        self.nodeDict = dict()
        self.assignments = []
        self.clauses = []
        self.allAssignments = []
        self.adjM = np.zeros((n*(n+1), n*(n+1)))#, dtype=int)
        for i in range(n+1):
            for j in range(n):
                self.nodeDict[(i,j)] = set()
        self.nodeToClauseDict = dict()
        for i in range(n+1):
            for j in range(n):
                self.nodeToClauseDict[(i,j)] = i*n+j
        self.clauses = []
        self.genClauses()

    def populateConnections(self):
        n=self.n
        for node in self.nodeDict.keys():
            i = node[0]
            j = node[1]
            # Handle row 0
            if i == n-1 and j == n-1:
                    self.nodeDict[node].add((2,1))    #node to bottom right
                    self.nodeDict[node].add((2,0))    #node to bottom left
                    self.nodeDict[node].add((n-2,n-1))    #node to top right
                    self.nodeDict[node].add((n-2,n-2))    #node to top left
            elif i == 0:
                if j == 0:
                    self.nodeDict[node].add((0,1))    #node to right
                    self.nodeDict[node].add((1,1))    #node to bottom right
                    self.nodeDict[node].add((1,0))    #node to lower bottom right
                    self.nodeDict[node].add((n,n-1))    #node above
                    for index in range(math.floor(n/2)+1):
                        self.nodeDict[node].add((n,index))    #nodes across bottom row
                elif j == n-1:
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                    self.nodeDict[node].add((n,n-1))    #node surrounding
                else:
                    self.nodeDict[node].add((n,n-1))    #node above
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                    self.nodeDict[node].add((i+1,j+1))    #node to bottom right
            # Handle row 1
            elif i == 1:
                if j == 0:
                    self.nodeDict[node].add((0,0))    #node to left
                    for index in range(math.floor(n/2), n):
                        self.nodeDict[node].add((n,index))    #nodes across bottom row
                elif j == 1:
                    self.nodeDict[node].add((0,0))    #node to left
                    self.nodeDict[node].add((i-1,j))    #node above
                    self.nodeDict[node].add((n,0))    #node to lower bottom left
                    self.nodeDict[node].add((n-1,0))    #node to lower bottom right
                    self.nodeDict[node].add((i+1,j+1))    #node to upper bottom right
                    self.nodeDict[node].add((i,j+1))    #node to right
                elif j == n-1:
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((n-i+1,j-(i-1)))    #node to lower bottom right
                    self.nodeDict[node].add((n-i, j-(i-1)-1))    #node to lower bottom left
                else:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                    self.nodeDict[node].add((i+1,j+1))    #node to bottom right
            # Handle row 2
            elif i == 2:
                if j == 0:
                    self.nodeDict[node].add((n-1,n-1))    #node to upper right
                    self.nodeDict[node].add((2,1))    #node to right
                    self.nodeDict[node].add((3,1))    #node to bottom right
                    self.nodeDict[node].add((3,0))    #node to bottom left
                    self.nodeDict[node].add((n-2,n-2))    #node above
                elif j == 1:
                    self.nodeDict[node].add((n-1,n-1))    #node to upper left
                    self.nodeDict[node].add((2,0))    #node to left
                    self.nodeDict[node].add((3,2))    #node to bottom right
                    self.nodeDict[node].add((3,1))    #node to bottom left
                    self.nodeDict[node].add((n-2,n-1))    #node above
                elif j == 2:
                    self.nodeDict[node].add((1,1))    #node to upper left
                    self.nodeDict[node].add((1,2))    #node to upper right
                    self.nodeDict[node].add((2,3))    #node to right
                    self.nodeDict[node].add((3,3))    #node to upper bottom right
                    self.nodeDict[node].add((n-j,0))    #node to lower bottom right
                    self.nodeDict[node].add((n-j+1,0))    #node to lower bottom left
                elif j == n-1:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i+1,j))    #node to upper bottom left
                    self.nodeDict[node].add((n-i,n-i-1))    #node to lower bottom left
                    self.nodeDict[node].add((n-i+1,n-i))    #node to lower bottom right
                else:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                    self.nodeDict[node].add((i+1,j+1))    #node to bottom right
            elif i == n:
                if j == 0:
                    self.nodeDict[node].add((0,0))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to bottom upper right
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((1,1))    #node to top upper right
                elif j == n-1:
                    self.nodeDict[node].add((1,0))    #node to bottom
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i-1,j-1))    #node to lower top left
                    self.nodeDict[node].add((1,n-1))    #node to middle top left
                    for index in range(n):
                        self.nodeDict[node].add((0,index))    #nodes across top row
                else:
                    if j <= math.floor(n/2):                   #node left of middle on bottom row
                        self.nodeDict[node].add((0,0))
                    if j >= math.floor(n/2):                   #node right of middle on bottom row
                        self.nodeDict[node].add((1,0))
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i,j+1))    #node to right
            else:
                if i == j:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((i+1,j+1))    #node to upper bottom right
                    self.nodeDict[node].add((n-i,0))    #node to lower bottom right
                    self.nodeDict[node].add((n-i+1,0))    #node to lower bottom left
                elif j == n-1:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i+1,j))    #node to upper bottom left
                    self.nodeDict[node].add((n-i,n-i-1))    #node to lower bottom left
                    self.nodeDict[node].add((n-i+1,n-i))    #node to lower bottom right
                elif j == 0:
                    self.nodeDict[node].add((n-i,n-i))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to bottom upper right
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((n-i+1,n-i+1))    #node to top upper right
                    self.nodeDict[node].add((i+1,j+1))    #node to bottom right
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                elif j == i - 1:
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                    self.nodeDict[node].add((i+1,j+1))    #node to bottom right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i-1,j-1))    #node to lower top left
                    self.nodeDict[node].add((n-i,n-1))    #node to upper top right
                    self.nodeDict[node].add((n-i+1,n-1))    #node to upper top left
                else:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                    self.nodeDict[node].add((i+1,j+1))    #node to bottom right
        for k, v in self.nodeDict.items():
            self.nodeDict[k]=sorted(v)

    def getLiteral(self, node, d):
        return d*(self.n*(self.n+1))+self.nodeToClauseDict[node]+1

    def getNode(self, literal):
        l=int((abs(literal)-1)%(self.n*(self.n+1)))
        return (math.floor(l/self.n), l%self.n)

    def getColor(self, literal):
        return math.floor(int((abs(literal)-1)/(self.n*(self.n+1))))

    def genClauses(self):
        self.populateConnections()
        self.generateAdjacencyMatrix()

        # (16) adjacent vertices have different colors
        for i in range(0,self.adjM.shape[0]):
            for j in range(i+1, self.adjM.shape[0]):
                if self.adjM[i][j]:
                    for k in range(self.d):
                        self.clauses.append([-self.getLiteral((self.getNode(i+1)), k), -self.getLiteral((self.getNode(j+1)), k)])

        # (15) Every vertex has at least one color
        for vertex in self.nodeDict.keys():
            self.clauses.append([self.getLiteral(vertex, k) for k in range(self.d)])

        if ('maxTwo' in self.variant):
            startLiteral = max([abs(x) for x in SATUtils.getUsedLiterals(self.clauses)]) + 1
            groups = []
            geResult = None
            for vertex in self.nodeDict.keys():
                # For each vertex, generate clauses that assert at least 2 colors are true
                geResult = SATUtils.atLeast([self.getLiteral(vertex, color) for color in range(self.d)], 2, startLiteral)
                groups.append(geResult[0])
                startLiteral = geResult[1]+1
            # pp.pprint(groups)
            maximized = SATUtils.atLeastRsub(groups, 1, startLiteral)
            # pp.pprint(maximized)
            self.clauses = maximized[0]




        # pp.pprint(self.clauses)
        #pp.pprint([[self.getNode(x) for x in y] for y in self.clauses])
        #pp.pprint([[self.getColor(x) for x in y] for y in self.clauses])

    def generateAdjacencyMatrix(self):
        for k,v in self.nodeDict.items():
            for edge in v:
                #self.adjM[k[0] * n + k[1]][edge[0] * n + edge[1]] = 1
                self.adjM[edge[0] * self.n + edge[1]][k[0] * self.n + k[1]] = 1

    def verifyCorrectness(self):
        N=self.n*(self.n + 1)
        n=self.n
        regions = 0
        edges = 0
        edgesSoFar = set()
        for k, v in self.nodeDict.items():
            regions+=1
            edges+=len(v)
            for edge in v:
                edgesSoFar.add(frozenset([k[0]*(n+1)+k[1], edge[0]*(n+1)+edge[1]]))
        edgesSoFar = [(math.floor(tuple(x)[0]/(n+1)),tuple(x)[0]%(n+1)) for x in edgesSoFar]
        # check that number of edges is correct
        if int(edges/2) != int(3*N-6):
            print(1, int(edges/2), int(3*N-6))
            return False
        # check that number of unique edges is correct
        elif len(edgesSoFar) != int(3*N-6):
            print(2, len(edgesSoFar), int(3*N-6))
            return False
        # check that number of vertices is correct
        elif regions != N:
            return False
        # check that adjacency matrix is symmetric
        for i in range(n+1):
            for j in range(n):
                if self.adjM[i][j] != self.adjM[j][i]:
                    return False
        return True

    def solve(self):
        self.assignments = pycosat.solve(self.clauses)
        if self.assignments == 'UNSAT':
            return False
        if self.doAll:
            self.allAssignments = list(pycosat.itersolve(self.clauses))
        return True

    def viewAssignments(self):
        validColors = dict()
        for literal in self.assignments:
            if literal > 0:
                if self.getNode(literal) not in validColors:
                    validColors[self.getNode(literal)] = set([self.getColor(literal)])
                else:
                    validColors[self.getNode(literal)].add(self.getColor(literal))
        return validColors

    @staticmethod
    def viewMinAssignments(n):
        mg = McGregor(n, 4)
        singleColorLiterals = list(filter(lambda x: mg.getColor(x) == 0, SATUtils.getUsedLiterals(mg.clauses)))
        newClauses = mg.clauses + SATUtils.atMost(inLiterals=singleColorLiterals,
                                                  r=McGregor.getBounds()[n][0],
                                                  startLiteral=len(SATUtils.getUsedLiterals(mg.clauses))+1)[0]
        #print(newClauses)
        return len(list(pycosat.itersolve(newClauses)))

    # f(n) smallest value of r that graph of order n can have some color r times.
    # g(n) largest value of r that graph of order n can have some color r times.
    # Problem 17
    @staticmethod
    def testLimits(bounds, viewProgress=False):
        limits = dict()
        for n in range(bounds[0], bounds[1]+1):
            if n == bounds[0]:
                r = 1
            else:
                r = limits[n-1][0]-1
            isF = True
            mg = McGregor(n, 4)
            # filter out all literals that are not color 0
            singleColorLiterals = list(filter(lambda x: mg.getColor(x) == 0, SATUtils.getUsedLiterals(mg.clauses)))
            while True: #repeat until upper bound is found
                if viewProgress:
                    print(r)
                if isF:
                    newClauses = SATUtils.atMost(singleColorLiterals, r, len(SATUtils.getUsedLiterals(mg.clauses))+1)[0]
                    newClauses = mg.clauses + newClauses
                    if (pycosat.solve(newClauses) != 'UNSAT'):
                        limits[n] = [r, -1]
                        if n != bounds[0]:
                            r = limits[n-1][1]-1
                        isF = False
                else:
                    newClauses = SATUtils.atLeast(singleColorLiterals, r, len(SATUtils.getUsedLiterals(mg.clauses))+1)[0]
                    newClauses = mg.clauses + newClauses
                    if (pycosat.solve(newClauses) == 'UNSAT'):
                        limits[n][1] = r-1
                        if viewProgress:
                            print(n, limits[n])
                        break
                r += 1
        return limits

    # h(n) largest number of regions that can be colored in 2 ways
    # Problem 19
    @staticmethod
    def testLimits(bounds, viewProgress=False):
        limits = dict()
        for n in range(bounds[0], bounds[1]+1):
            if n == bounds[0]:
                r = 1
            else:
                r = limits[n-1][0]-1
            isF = True
            mg = McGregor(n, 4)
            # filter out all literals that are not color 0
            singleColorLiterals = list(filter(lambda x: mg.getColor(x) == 0, SATUtils.getUsedLiterals(mg.clauses)))
            while True: #repeat until upper bound is found
                if viewProgress:
                    print(r)
                if isF:
                    newClauses = SATUtils.atMost(singleColorLiterals, r, len(SATUtils.getUsedLiterals(mg.clauses))+1)[0]
                    newClauses = mg.clauses + newClauses
                    if (pycosat.solve(newClauses) != 'UNSAT'):
                        limits[n] = [r, -1]
                        if n != bounds[0]:
                            r = limits[n-1][1]-1
                        isF = False
                else:
                    newClauses = SATUtils.atLeast(singleColorLiterals, r, len(SATUtils.getUsedLiterals(mg.clauses))+1)[0]
                    newClauses = mg.clauses + newClauses
                    if (pycosat.solve(newClauses) == 'UNSAT'):
                        limits[n][1] = r-1
                        if viewProgress:
                            print(n, limits[n])
                        break
                r += 1
        return limits

    @staticmethod
    def getBounds():
        bounds = {3: [2, 4],
                  4: [2, 6],
                  5: [3, 10],
                  6: [4, 13],
                  7: [5, 17],
                  8: [7, 23],
                  9: [7, 28],
                  10: [7, 35],
                  11: [8, 42],
                  12: [9, 50],
                  13: [10, 58],
                  14: [12, 68],
                  15: [12, 77],
                  16: [12, 88],
                  17: [13, 99],
                  18: [14, 111],
                  19: [15, 123],
                  20: [17, 137],
                  21: [17, 150],
                  22: [17, 165],
                  23: [18, 180],
                  24: [19, 196]
                  }
        return bounds



if __name__ == "__main__":
    mGreg = McGregor(n=3, d=4, all=False)
    # McGregor.testLimits([17, 26])

    if mGreg.solve():
        pp.pprint(mGreg.nodeDict)
        print(mGreg.verifyCorrectness())
        #print(len(mg.clauses))
        #print(mg.viewAssignments())
        #print(mg.assignments)
        #print(len(mg.allAssignments))
    else:
        print('UNSAT')

    # literals = [x+0 for x in range(1, 10+1)]
    # su = SATUtils.atMost(literals, 7)
    # pp.pprint(pycosat.solve(su[0] + [[-1], [-2], [-3], [-4], [-5]]))
    # print(su)
    # clauses, mapping = SATUtils.rewriteFrom1toN(su[0])
    # pp.pprint(clauses)
    # allSolutions = list(pycosat.itersolve(clauses+[[1], [-2], [-3] ]))
    # pp.pprint(allSolutions)
    # tmpSolutions = [SATUtils.applyLiteralMapping(clauses, mapping) for solution in allSolutions]
    # print(tmpSolutions)