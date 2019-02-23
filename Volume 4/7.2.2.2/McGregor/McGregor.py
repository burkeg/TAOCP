import pycosat
import math
import numpy as np
import pprint as pp
import sys
import collections

class McGregor:
    def  __init__(self, n, d, all=False):
        if (n < 3):
            raise ValueError()
        self.fname = "McGregorAssignments_" + str(n) + ".txt"
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
        return d*(n*(n+1))+self.nodeToClauseDict[node]+1

    def getNode(self, literal):
        l=int((abs(literal)-1)%(self.n*(self.n+1)))
        return (math.floor(l/n), l%n)

    def getColor(self, literal):
        return math.floor(int((abs(literal)-1)/(self.n*(self.n+1))))

    def genClauses(self):
        self.populateConnections()
        self.generateAdjacencyMatrix()
        # (15) Every vertex has at least one color
        for vertex in self.nodeDict.keys():
            self.clauses.append([self.getLiteral(vertex, k) for k in range(d)])

        # (16) adjacent vertices have different colors
        for i in range(0,self.adjM.shape[0]):
            for j in range(i+1, self.adjM.shape[0]):
                if self.adjM[i][j]:
                    for k in range(self.d):
                        self.clauses.append([-self.getLiteral((self.getNode(i+1)), k), -self.getLiteral((self.getNode(j+1)), k)])


        pp.pprint(self.clauses)
        #pp.pprint([[self.getNode(x) for x in y] for y in self.clauses])
        #pp.pprint([[self.getColor(x) for x in y] for y in self.clauses])

    def generateAdjacencyMatrix(self):
        for k,v in self.nodeDict.items():
            for edge in v:
                #self.adjM[k[0] * n + k[1]][edge[0] * n + edge[1]] = 1
                self.adjM[edge[0] * n + edge[1]][k[0] * n + k[1]] = 1

    def verifyCorrectness(self):
        N=self.n*(self.n + 1)
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

    def testLimits(self):
        originalClauses = self.clauses
        

class SATUtils:
    # applies a mapping from one literal to another
    @staticmethod
    def applyLiteralMapping(clauses, mapping, oldToNew=True):
        tmp_map = mapping
        if oldToNew:
            tmp_map = {v: k for k, v in mapping.items()}
        return [[int(x/abs(x))*tmp_map[abs(x)] for x in clause] for clause in clauses]

    #returns a tuple containing:
    # an equivalent list of clauses with literals 1-n
    # the mapping from old literals to new literals
    @staticmethod
    def rewriteFrom1toN(clauses):
        usedLiterals = SATUtils.getUsedLiterals(clauses)
        literalMapping = dict()
        count = 1
        for literal in usedLiterals:
            literalMapping[abs(literal)] = count
            count += 1
        return([[int(x/abs(x))*literalMapping[abs(x)] for x in clause] for clause in clauses], literalMapping)

    # returns the set of literals used in the clauses
    @staticmethod
    def getUsedLiterals(clauses):
        usedLiterals = set()
        for clause in clauses:
            for literal in clause:
                usedLiterals.add(abs(literal))
        return usedLiterals

    # given a set of literals and r, this produces a set of clauses that is
    # only SAT when exactly r terms are true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    @staticmethod
    def exactly(inLiterals, r, startLiteral = None):
        geResult = SATUtils.atLeast(inLiterals, 2, startLiteral)
        clauses = geResult[0]
        ltResult = SATUtils.atMost(inLiterals, 2, geResult[1] + 1)
        clauses = clauses + ltResult[0]
        return (clauses, ltResult[1])

    # given a set of literals and r, this produces a set of clauses that is
    # only SAT when at least r terms are true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    @staticmethod
    def atLeast(inLiterals, r, startLiteral = None):
        inLiterals = [-x for x in inLiterals]
        return SATUtils.atMost(inLiterals, len(inLiterals) - r, startLiteral)

    # given a set of literals and r, this produces a set of clauses that is
    # only SAT when at most r terms are true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    @staticmethod
    def atMost(inLiterals, r, startLiteral = None):
        if startLiteral == None:
            startLiteral = max([abs(x) for x in inLiterals]) + 1
        n=len(inLiterals)
        clauses = []
        # format:
        # 2-tuple means use x[tuple[1]] with polarity tuple[0]
        # 3-tuple means create variable tuple[0]*s^tuple[2]_tuple[1]

        for k in range(1, r+1):
            for j in range(1, n-r):
                clauses.append([(-1, j, k), (1, j+1, k)])

        for k in range(0, r+1):
            for j in range(1, n-r+1):
                if k == 0:
                    clauses.append([(-1, j+k), (1, j, k+1)])
                elif k == r:
                    clauses.append([(-1, j+k), (-1, j, k)])
                else:
                    clauses.append([(-1, j+k), (-1, j, k), (1, j, k+1)])

        # determine max j
        maxSubscript = -sys.maxsize - 1
        minSubscript = sys.maxsize
        maxSuperscript = -sys.maxsize - 1
        minSuperscript = sys.maxsize
        for clause in clauses:
            for literal in clause:
                # only look at new variables
                if len(literal) != 2:
                    maxSubscript = literal[1] if literal[1] > maxSubscript else maxSubscript
                    minSubscript = literal[1] if literal[1] < minSubscript else minSubscript
                    maxSuperscript = literal[2] if literal[2] > maxSuperscript else maxSuperscript
                    minSuperscript = literal[2] if literal[2] < minSuperscript else minSuperscript

        # rewrite new variables from tuples to literals
        for i in range(len(clauses)):
            for j in range(len(clauses[i])):
                # don't process x's yet, only handle s's
                if len(clauses[i][j]) != 2:
                                                #sign of literal
                    clauses[i][j] = clauses[i][j][0]*( \
                                    # Offset from input set of literals
                                startLiteral + \
                                    # Convert the subscript and superscripts into the index of a flattened
                                    # 2d array. Adjusted so each dimension is 0-indexed
                                (clauses[i][j][2]-minSuperscript)*(maxSubscript-minSubscript+1) + \
                                (clauses[i][j][1]-minSubscript))
                else:
                    clauses[i][j] = clauses[i][j][0]*inLiterals[clauses[i][j][1]-1]
        #print(maxSubscript)
        largestLiteral = max([max([abs(x) for x in clause]) for clause in clauses])
        return (clauses, largestLiteral)



if __name__ == "__main__":
    n=10
    d=4
    mg = McGregor(n=n, d=d, all=False)
    if mg.solve():
        pp.pprint(mg.nodeDict)
        print(mg.verifyCorrectness())
        #print(len(mg.clauses))
        #print(mg.viewAssignments())
        #print(mg.assignments)
        #print(len(mg.allAssignments))
    else:
        print('UNSAT')
    # literals = [x+0 for x in [1, 2, 3, 4]]
    # su = SATUtils.exactly(literals, 2, 1000)
    # clauses, mapping = SATUtils.rewriteFrom1toN(su[0])
    # pp.pprint(clauses)
    # allSolutions = list(pycosat.itersolve(clauses+[[1], [-2], [-3] ]))
    # pp.pprint(allSolutions)
    # tmpSolutions = [SATUtils.applyLiteralMapping(clauses, mapping) for solution in allSolutions]
    # print(tmpSolutions)