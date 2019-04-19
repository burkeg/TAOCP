from McGregor import McGregor
from SATUtils import SATUtils, CNF, Clause, Literal, DSAT
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
    # revisted after adding some new utilities

    neighbors = GraphColoring.invert(GraphColoring.strongProduct(GraphColoring.C(5), GraphColoring.C(5)))
    pp.pprint(neighbors)
    for maxColors in range(1, 26):
        GC = GraphColoring(neighbors, maxColors)
        GC.defineNodeLiteralConversion(literalToID=(lambda x: (((x - 1) % 25) // 5, (x - 1) % 5)),
                                       literalToColor=     (lambda x: (x-1) // 25),
                                       GraphNodeToLiteral=      (lambda indexTuple, color: indexTuple[0] * 5 + indexTuple[1] + 25 * color + 1))
        GC.generateClauses()
        solution = pycosat.solve(GC.clauses)
        if 'UNSAT' != solution:
            print(maxColors)
            print(solution)
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

    # A double coloring is where two distinct colors to every vertex so no two vertices
    # that share an edge don't share a color. A q-tuple coloring assigns q distinct colors
    # in the same way. Find double and triple colorings of cycle graphs C5, C7, ... using
    # as few colors as possible
def Exercise33():
    solutions = dict()
    dlim = 50
    for minColors in range(2,7):
        for n in range(3, 20, 2):
            for d in range(minColors, dlim+1):
                graphColorer = GraphColoring(nodeDict=GraphColoring.C(n),
                                             d=d,
                                             minColors=minColors,
                                             adjacentDifColor=1)
                graphColorer.defineNodeLiteralConversion(\
                                            literalToID=(lambda x: ((x - 1) % n)),
                                            literalToColor=     (lambda x: (x-1) // n),
                                            GraphNodeToLiteral=      (lambda indexTuple, color: indexTuple + n * color + 1))
                graphColorer.generateClauses()
                solution = pycosat.solve(graphColorer.clauses)
                # graphColorer.viewClauses()
                if 'UNSAT' != solution:
                    # pp.pprint(GC.clauses)
                    print('--Success--')
                    print('n: ' + str(n))
                    print('minColors: ' + str(minColors))
                    print('d: ' + str(d))
                    solutions[(n, minColors, d)] = solution
                    print('--------------------------------------------')
                    break
                else:
                    print('--UNSAT--')
                    print('n: ' + str(n))
                    print('minColors: ' + str(minColors))
                    print('d: ' + str(d))
                    if d == dlim:
                        print('Giving up!')
                        solutions[(n, minColors, None)] = solution

    # pp.pprint(list(solutions.values()))
    print('(n, minColors, d)')
    pp.pprint(list(solutions.keys()))

    # A radio coloring is where each pair of verticies u-v have at least 2 colors that are different
    # and where any u-v were there exists a vertex w s.t. w-u and w-v, u,v, and w have at least 1 color
    # that differs
    #
    # This solution solved a different problem than what Knuth intended. I misunderstood the problem.
    # My understanding was that each node has multiple "channels", and each neighboring node had to have
    # at least 2 unique "channels" that none of its neighbors shared. Likewise nodes that share a neighbor
    # need at least 1 unique channel that none of its neighbor's neighbors had.
    # The real world equivalent of that would be that each station would have at least 2 channels that
    # had no strong interference and at least 1 channel that
def Exercise36misunderstood():
    # 2 parts: first of all, how do I assert 2 nodes differ by k colors?
    # second, find all 3+cliques. For each u-v, if v is in a 3+clique with u, assert 1 diff, else assert 2 diff
    d=10
    n=3
    graphColorer = GraphColoring(nodeDict=McGregor(n,d).nodeDict,
                                 d=d,
                                 adjacentDifColor=0,
                                 minColors=1)
    graphColorer.defineNodeLiteralConversion(\
                                   literalToID=(lambda x: (((x - 1) % (n + 1) ** 2) // (n + 1), (x - 1) % (n + 1))),
                                   literalToColor=     (lambda x: (x-1) // (n+1)**2),
                                   GraphNodeToLiteral=      (lambda indexTuple, color: indexTuple[0] * (n + 1) + indexTuple[1] + ((n + 1) ** 2) * color + 1))
    graphColorer.generateClauses()
    for i, A in enumerate(graphColorer.nodeDict):
        for j, B in enumerate(graphColorer.nodeDict):
            if j <= i:
                continue
            if graphColorer.sharesNeighbor(A, B):
                if graphColorer.isAdjacent(A, B):
                    graphColorer.assertRdiffColors(A,B,1)
                else:
                    graphColorer.assertRdiffColors(A,B,2)
    pp.pprint(graphColorer.clauses)
    pp.pprint(list(pycosat.solve(graphColorer.clauses)))
    graphColorer.viewSolution()

    # A radio coloring is where each pair of verticies u-v have at least 2 colors that are different
    # and where any u-v were there exists a vertex w s.t. w-u and w-v, u,v, and w have at least 1 color
    # that differs
def Exercise36():
    d=16
    n=10
    graphColorer = GraphColoring(nodeDict=McGregor(n,d).nodeDict,
                                 d=d,
                                 adjacentDifColor=None,
                                 minColors=1)
    graphColorer.defineNodeLiteralConversion()
        #                            literalToID=(lambda x: (((x - 1) % (n + 1) ** 2) // (n + 1), (x - 1) % (n + 1))),
        #                            literalToColor=     (lambda x: (x-1) // (n+1)**2),
        #                            GraphNodeToLiteral=      (lambda indexTuple, color: indexTuple[0] * (n + 1) + indexTuple[1] + ((n + 1) ** 2) * color + 1))
    graphColorer.generateClauses()
    graphColorer.L(2, 1)
    # pp.pprint(graphColorer.clauses)
    # pp.pprint(list(pycosat.solve(graphColorer.clauses)))
    # # graphColorer.viewSolution()
    # graphColorer.cnf.mergeWithRaw(graphColorer.clauses)
    # DSAT(graphColorer.cnf).printCNF()
    graphColorer.viewSolution()


def Exercise36ScratchPad():
    d=4
    n=2
    graphColorer = GraphColoring(nodeDict=GraphColoring.cartesianProduct(GraphColoring.C(n), GraphColoring.C(n)),
                                 d=d,
                                 adjacentDifColor=None,
                                 minColors=1,
                                 maxColors=1)
    graphColorer.defineNodeLiteralConversion()
        #                            literalToID=(lambda x: (((x - 1) % (n + 1) ** 2) // (n + 1), (x - 1) % (n + 1))),
        #                            literalToColor=     (lambda x: (x-1) // (n+1)**2),
        #                            GraphNodeToLiteral=      (lambda indexTuple, color: indexTuple[0] * (n + 1) + indexTuple[1] + ((n + 1) ** 2) * color + 1))
    graphColorer.generateClauses()
    graphColorer.L(2, 1)
    # pp.pprint(graphColorer.clauses)
    # pp.pprint(list(pycosat.solve(graphColorer.clauses)))
    graphColorer.cnf.mergeWithRaw(graphColorer.clauses)
    DSAT(graphColorer.cnf).printCNF()
    graphColorer.viewSolutions()

    # Find the optimum radio coloring of the contiguous USA graph
def Exercise37():
    d=10 #10 is the minimum number of colors that is still SAT
    graphColorer = GraphColoring(nodeDict=GraphColoring.US(contiguous=True),
                                 d=d,
                                 adjacentDifColor=None,
                                 minColors=1,)
    graphColorer.defineNodeLiteralConversion()
    graphColorer.generateClauses()
    graphColorer.L(2, 1)
    graphColorer.cnf.mergeWithRaw(graphColorer.clauses)
    DSAT(graphColorer.cnf).printCNF()
    graphColorer.viewSolution()

    # Find the optimum radio coloring
    # a) P_n [] P_n
def Exercise38a():
    d=7 #10 is the minimum number of colors that is still SAT
    n=8
    graphColorer = GraphColoring(nodeDict=GraphColoring.cartesianProduct(GraphColoring.P(n), GraphColoring.P(n)),
                                 d=d,
                                 adjacentDifColor=None,
                                 minColors=1,)
    graphColorer.defineNodeLiteralConversion()
    graphColorer.generateClauses()
    graphColorer.L(2, 1)
    graphColorer.cnf.mergeWithRaw(graphColorer.clauses)
    DSAT(graphColorer.cnf).printCNF()
    graphColorer.viewSolution()

if __name__ == "__main__":
    Exercise38a()