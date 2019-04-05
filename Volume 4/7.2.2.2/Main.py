from McGregor import McGregor
from SATUtils import SATUtils
from GraphColoring import GraphColoring
import pycosat
import math
import numpy as np
import pprint as pp

def Exercise17():
    print(McGregor.testLimits([3, 10], viewProgress=True))

def Exercise18():
    for i in range(3,20):
        print(i, int(McGregor.viewMinAssignments(i) / 6))

def Exercise19ScratchPad():
    # This is my trying to add some new literal -l to each clause within a grouping.
    # If those original clauses were already satisfiable then forcing l to true should
    # still be satifiable. If they weren't then they would HAVE to assign l to false.
    # I add one more clause that asserts r of those k auxiliary literals are true.
    exclusions = [[-1], [-2], [-3], [-9], [-10]]
    clauses1 = [1, 2, 3, 4]
    # pp.pprint(list(clauses1))
    geResult = SATUtils.atLeast(clauses1, 2)
    clauses1 = geResult[0]
    clauses2 = range(geResult[1]+1, geResult[1]+5)
    # pp.pprint(list(clauses2))
    geResult = SATUtils.atLeast(clauses2, 3)
    clauses2 = geResult[0]
    clauses3 = range(geResult[1]+1, geResult[1]+5)
    # pp.pprint(list(clauses3))
    geResult = SATUtils.atLeast(clauses3, 2)
    clauses3 = geResult[0]
    # pp.pprint(list(clauses1))
    # pp.pprint(list(clauses2))
    # pp.pprint(list(clauses3))
    newVars = range(geResult[1]+1, geResult[1]+4)
    # pp.pprint(list(newVars))
    clauses1 = [x + [-newVars[0]] for x in clauses1]
    clauses2 = [x + [-newVars[1]] for x in clauses2]
    clauses3 = [x + [-newVars[2]] for x in clauses3]
    # pp.pprint(list(clauses1))
    # pp.pprint(list(clauses2))
    # pp.pprint(list(clauses3))
    geResult = SATUtils.atLeast(newVars, 3)
    maximized = geResult[0]
    # pp.pprint(list(maximized))

    pp.pprint(list(clauses1))
    pp.pprint(list(clauses2))
    pp.pprint(list(clauses3))
    pp.pprint(list(maximized))
    # pp.pprint(list(exclusions))
    # pp.pprint(list(pycosat.solve(clauses1 + clauses2 + clauses3 + maximized + exclusions)))

    clauses1 = [1, 2, 3, 4]
    geResult = SATUtils.atLeast(clauses1, 2)
    clauses1 = geResult[0]
    clauses2 = range(geResult[1]+1, geResult[1]+5)
    geResult = SATUtils.atLeast(clauses2, 3)
    clauses2 = geResult[0]
    clauses3 = range(geResult[1]+1, geResult[1]+5)
    geResult = SATUtils.atLeast(clauses3, 2)
    clauses3 = geResult[0]
    pp.pprint(SATUtils.atLeastRsub([clauses1, clauses2, clauses3], 3))

def Exercise19():
    # Exercise19ScratchPad()
    for i in range(8, 30):
        print('i: ', i)
        tst = McGregor(i,4)
        tst.maximize2ColoredRegions([0, 100000])
        print('________')
    # tst.solve()
    # pp.pprint(tst.assignments)
    # pp.pprint([(tst.getNode(x), tst.getColor(x), x)  for x in tst.assignments])
    pass

def Exercise21ScratchPad():
    result = SATUtils.exactlyOne([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], )
    pp.pprint(result)
    result = result[0] + []
    result = SATUtils.rewriteFrom1toN(result)
    # pp.pprint(result)
    pp.pprint(list(pycosat.itersolve(result[0])))


def Exercise21():
    MGGraph = McGregor(10, 2)
    MGGraph.minimizeKernel([17, 18])
    pp.pprint([MGGraph.getNode(x) for x in MGGraph.assignments if x>0 and abs(x) <= MGGraph.n*(MGGraph.n+1)])


def Exercise22ScratchPad():
    # neighbors = dict()
    # for i in range(5):
    #     for j in range(5):
    #         key = (i, j)
    #         neighbors[key] = [((i + 1) % 5, (j + 1) % 5),
    #          ((i + 1) % 5, (j + 0) % 5),
    #          ((i + 1) % 5, (j - 1) % 5),
    #          ((i - 1) % 5, (j + 1) % 5),
    #          ((i - 1) % 5, (j + 0) % 5),
    #          ((i - 1) % 5, (j - 1) % 5),
    #          ((i + 0) % 5, (j + 1) % 5),
    #          ((i + 0) % 5, (j - 1) % 5)]
    # pp.pprint(neighbors)
    n=4
    d=4
    MG = McGregor(n, d)
    GC = GraphColoring(MG.nodeDict, d)
    GC.defineNodeLiteralConversion(MG.getLiteralToIndexTupleFunc(), MG.getLiteralToColorFunc(), MG.getNodeToLiteralFunc())
    GC.constraints |= GC.constraint_minOneColor | GC.constraint_adjacentDifColor
    GC.generateClauses()
    pp.pprint(GC.clauses)
    pp.pprint(MG.clauses)

def Exercise22():
    neighbors = dict()
    allElems = set([(x, y) for x in range(5) for y in range(5)])
    # generate adjacency list that corresponds to a torus
    for i in range(5):
        for j in range(5):
            key = (i, j)
            excludedElems = set()
            excludedElems.add(((i + 1) % 5, (j + 1) % 5))
            excludedElems.add(((i + 1) % 5, (j + 0) % 5))
            excludedElems.add(((i + 1) % 5, (j - 1) % 5))
            excludedElems.add(((i - 1) % 5, (j + 1) % 5))
            excludedElems.add(((i - 1) % 5, (j + 0) % 5))
            excludedElems.add(((i - 1) % 5, (j - 1) % 5))
            excludedElems.add(((i + 0) % 5, (j + 1) % 5))
            excludedElems.add(((i + 0) % 5, (j + 0) % 5))
            excludedElems.add(((i + 0) % 5, (j - 1) % 5))
            neighbors[key] = list(allElems.difference(excludedElems))
            # print(excludedElems)
            # print(neighbors[key])
            # print('---------------------')
    pp.pprint(neighbors)
    for maxColors in range(1, 26):
        GC = GraphColoring(neighbors, maxColors)
        GC.defineNodeLiteralConversion((lambda x: ((x-1) // 5, (x-1) % 5)),
                                       (lambda x: (x-1) // 25),
                                       (lambda indexTuple, color: indexTuple[0]*5+indexTuple[1]+25*color+1))
        GC.constraints |= GC.constraint_minOneColor | GC.constraint_adjacentDifColor
        GC.generateClauses()
        solution = pycosat.solve(GC.clauses)
        if 'UNSAT' != solution:
            # pp.pprint(GC.clauses)
            print(maxColors)
            print(solution)
            # print(list(pycosat.itersolve(GC.clauses)))
            # print(len(list(pycosat.itersolve(GC.clauses))))
            return
        else:
            print(solution)
            print(maxColors)

def Exercise31():
    def F(t, r):
        n = r
        firstTime = True
        while True:
            clauses = SATUtils.waerden(n+1,t,n) + SATUtils.exactlyR(range(1, n+1), r)[0]
            if pycosat.solve(clauses) != 'UNSAT':
                if firstTime:
                    return n
                return n
            n += 1
            firstTime = False
    for t in range(3, 7):
        for r in range(1, 28):
            print(F(t, r))#, end=', ')
        print('')

if __name__ == "__main__":
    Exercise31()