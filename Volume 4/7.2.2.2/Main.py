from McGregor import McGregor
from SATUtils import SATUtils
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
    tst = McGregor(4,4,variant='maxTwo')
    tst.solve()
    pp.pprint(tst.assignments)
    pass

if __name__ == "__main__":
    Exercise19()