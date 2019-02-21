import pycosat
import math
import numpy as np
import pprint as pp
import collections
class McGregor:
    def  __init__(self, n, d):
        if (n < 3):
            raise ValueError()
        self.fname = "McGregorAssignments_" + str(n) + ".txt"
        self.n = n
        self.d = d
        self.nodeDict = dict()
        self.assignments = []
        self.clauses = []
        self.adjM = np.zeros((n*(n+1), n*(n+1)))#, dtype=int)
        for i in range(n+1):
            for j in range(n):
                self.nodeDict[(i,j)] = set()
        self.nodeToClauseDict = dict()
        for i in range(n+1):
            for j in range(n):
                self.nodeToClauseDict[(i,j)] = i*n+j
        self.clauses = []

    def populateConnections(self):
        n=self.n
        for node in self.nodeDict.keys():
            i = node[0]
            j = node[1]
            # Handle row 0
            if i is n-1 and j is n-1:
                    self.nodeDict[node].add((2,1))    #node to bottom right
                    self.nodeDict[node].add((2,0))    #node to bottom left
                    self.nodeDict[node].add((n-2,n-1))    #node to top right
                    self.nodeDict[node].add((n-2,n-2))    #node to top left
            elif i is 0:
                if j is 0:
                    self.nodeDict[node].add((0,1))    #node to right
                    self.nodeDict[node].add((1,1))    #node to bottom right
                    self.nodeDict[node].add((1,0))    #node to lower bottom right
                    self.nodeDict[node].add((n,n-1))    #node above
                    for index in range(math.floor(n/2)+1):
                        self.nodeDict[node].add((n,index))    #nodes across bottom row
                elif j is n-1:
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
            elif i is 1:
                if j is 0:
                    self.nodeDict[node].add((0,0))    #node to left
                    for index in range(math.floor(n/2), n):
                        self.nodeDict[node].add((n,index))    #nodes across bottom row
                elif j is 1:
                    self.nodeDict[node].add((0,0))    #node to left
                    self.nodeDict[node].add((i-1,j))    #node above
                    self.nodeDict[node].add((n,0))    #node to lower bottom left
                    self.nodeDict[node].add((n-1,0))    #node to lower bottom right
                    self.nodeDict[node].add((i+1,j+1))    #node to upper bottom right
                    self.nodeDict[node].add((i,j+1))    #node to right
                elif j is n-1:
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
            elif i is 2:
                if j is 0:
                    self.nodeDict[node].add((n-1,n-1))    #node to upper right
                    self.nodeDict[node].add((2,1))    #node to right
                    self.nodeDict[node].add((3,1))    #node to bottom right
                    self.nodeDict[node].add((3,0))    #node to bottom left
                    self.nodeDict[node].add((n-2,n-2))    #node above
                elif j is 1:
                    self.nodeDict[node].add((n-1,n-1))    #node to upper left
                    self.nodeDict[node].add((2,0))    #node to left
                    self.nodeDict[node].add((3,2))    #node to bottom right
                    self.nodeDict[node].add((3,1))    #node to bottom left
                    self.nodeDict[node].add((n-2,n-1))    #node above
                elif j is 2:
                    self.nodeDict[node].add((1,1))    #node to upper left
                    self.nodeDict[node].add((1,2))    #node to upper right
                    self.nodeDict[node].add((2,3))    #node to right
                    self.nodeDict[node].add((3,3))    #node to upper bottom right
                    self.nodeDict[node].add((n-j,0))    #node to lower bottom right
                    self.nodeDict[node].add((n-j+1,0))    #node to lower bottom left
                elif j is n-1:
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
            elif i is n:
                if j is 0:
                    self.nodeDict[node].add((0,0))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to bottom upper right
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((1,1))    #node to top upper right
                elif j is n-1:
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
                if i is j:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((i+1,j+1))    #node to upper bottom right
                    self.nodeDict[node].add((n-i,0))    #node to lower bottom right
                    self.nodeDict[node].add((n-i+1,0))    #node to lower bottom left
                elif j is n-1:
                    self.nodeDict[node].add((i-1,j-1))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to upper right
                    self.nodeDict[node].add((i,j-1))    #node to left
                    self.nodeDict[node].add((i+1,j))    #node to upper bottom left
                    self.nodeDict[node].add((n-i,n-i-1))    #node to lower bottom left
                    self.nodeDict[node].add((n-i+1,n-i))    #node to lower bottom right
                elif j is 0:
                    self.nodeDict[node].add((n-i,n-i))    #node to upper left
                    self.nodeDict[node].add((i-1,j))    #node to bottom upper right
                    self.nodeDict[node].add((i,j+1))    #node to right
                    self.nodeDict[node].add((n-i+1,n-i+1))    #node to top upper right
                    self.nodeDict[node].add((i+1,j+1))    #node to bottom right
                    self.nodeDict[node].add((i+1,j))    #node to bottom left
                elif j is i - 1:
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
                        self.clauses.append([-self.getLiteral((self.getNode(i)), k), -self.getLiteral((self.getNode(j)), k)])


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
        if int(edges/2) is not 3*N-6:
            return False
        # check that number of unique edges is correct
        elif len(edgesSoFar) is not 3*N-6:
            return False
        # check that number of vertices is correct
        elif regions is not N:
            return False
        # check that adjacency matrix is symmetric
        for i in range(n+1):
            for j in range(n):
                if self.adjM[i][j] != self.adjM[j][i]:
                    return False
        return True

    def solve(self):
        self.genClauses()
        self.assignments = pycosat.solve(self.clauses)
        return self.assignments != 'UNSAT'

    def viewAssignments(self):
        validColors = dict()
        for literal in self.assignments:
            if literal > 0:
                if self.getNode(literal) not in validColors:
                    validColors[self.getNode(literal)] = set([self.getColor(literal)])
                else:
                    validColors[self.getNode(literal)].add(self.getColor(literal))
        return validColors

if __name__ == "__main__":
    #solve('small_instances.txt')
    n=3
    d=4
    mg = McGregor(n=n, d=d)
    if mg.solve():
        #pp.pprint(mg.nodeDict)
        print(mg.verifyCorrectness())
        print(len(mg.clauses))
        print(mg.viewAssignments())
    else:
        print('UNSAT')