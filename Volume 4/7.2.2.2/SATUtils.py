import sys
import pprint as pp
import copy
import operator as op
import pycosat
from functools import reduce
import itertools

sign = lambda x: x and (1, -1)[x < 0]

class CNF:
    def __init__(self, clauses=[]):
        # Make sure the incoming clauses are all Clause objects. If a list of integers
        # is passed in, this should create a list of Clause objects with the same values
        # and empty comments
        self.clauses = [x if type(x) is Clause else Clause(x) for x in clauses]

    def rawCNF(self):
        return [[literal.value for literal in clause.literals] for clause in self.clauses]

    def addClause(self, clause):
        self.clauses.append(clause)

    def mergeWithRaw(self, newCNF, allowDuplicates=True):
        if allowDuplicates:
            for clause in newCNF:
                newClause = Clause([])
                for literal in clause:
                    newClause.addLiteral(Literal(literal))
                self.addClause(newClause)
        else:
            currentCNF = self.rawCNF()
            for clause in newCNF:
                if set(clause) not in [set(x) for x in currentCNF]:
                    newClause = Clause([])
                    for literal in clause:
                        newClause.addLiteral(Literal(literal))
                    self.addClause(newClause)

    def usedVariables(self):
        varSet = set()
        for clause in self.rawCNF():
            for literal in clause:
                varSet.add(abs(literal))
        return varSet


class Clause:
    def __init__(self, literals=[], comment = '_', groupComment = '_'):
        self.comment = comment
        self.groupComment = groupComment
        # Make sure the incoming literals are all Literal objects. If a list of integers
        # is passed in, this should create a list of Literal objects with the same values
        # and empty comments
        self.literals = [x if type(x) is Literal else Literal(x) for x in literals]

    def addLiteral(self, literal):
        self.literals.append(literal)


class Literal:
    def __init__(self, literal, comment = '_'):
        self.value = literal
        self.comment = comment

# class for debugging SAT problems
class DSAT:
    def __init__(self, cnf):
        self.cnf = cnf

    def printCNF(self):
        sorted_input = sorted(self.cnf.clauses, key=lambda x: x.groupComment)
        groups = itertools.groupby(sorted_input, key=lambda x: x.groupComment)
        for k, v in groups:
            print('Group Description: ' + k)
            for clause in v:
                print('\tClause Description: ' + clause.comment)
                for literal in clause.literals:
                    print('\t\t'+str(literal.value) + ': ' + literal.comment)

    def rawCNF(self):
        self.cnf.rawCNF()

    # View a new set of clauses based on a partial assignment. You can optionally propagate unit clauses
    # recursively to see if any trivial contradictions arise.
    def viewClausesAfterPartialAssignment(self, partialAssignment, propagateUnitClauses = True, cnf=None, verbose = False):
        if cnf == None:
            cnf = copy.deepcopy(self.cnf)

        if verbose:
            DSAT(cnf).printCNF()
            print('-------------------------\nAssigning:' + str(partialAssignment) + '\n')

        # prune clauses containing matching polarity literals to the partal assignment
        for i in range(len(cnf.clauses)-1, -1, -1):
            clauseDeleted=False
            for literal in partialAssignment:
                if clauseDeleted:
                    break
                for j in range(len(cnf.clauses[i].literals)-1, -1, -1):
                    # delete clauses when the literal matches, since that clause is now satisfied
                    if literal == cnf.clauses[i].literals[j].value:
                        del cnf.clauses[i]
                        clauseDeleted = True
                        break
                    # delete literals of opposite polarity since that literal can no longer satisfy that clause
                    if -literal == cnf.clauses[i].literals[j].value:
                        del cnf.clauses[i].literals[j]
        if propagateUnitClauses:
            for clause in cnf.clauses:
                # If an empty clause exists, that means the partial assignment is UNSAT
                if len(clause.literals) == 0:
                    print('Partial assignment forces UNSAT!')
                    return
                # If a unit clause exists, recursively compute
                if len(clause.literals) == 1:
                    self.viewClausesAfterPartialAssignment(partialAssignment + [clause.literals[0].value],
                                                           propagateUnitClauses = True,
                                                           cnf=cnf,
                                                           verbose=verbose)
                    return
            DSAT(cnf).printCNF()
        else:
            DSAT(cnf).printCNF()


class SATUtils:
    @staticmethod
    def nCr(n, r):
        r = min(r, n-r)
        numer = reduce(op.mul, range(n, n-r, -1), 1)
        denom = reduce(op.mul, range(1, r+1), 1)
        return numer / denom

    # applies a mapping from one literal to another
    @staticmethod
    def applyLiteralMapping(clauses, mapping, oldToNew=True):
        tmp_map = mapping
        if oldToNew:
            tmp_map = {v: k for k, v in mapping.items()}
        return [[int(x/abs(x))*tmp_map[abs(x)] for x in clause] for clause in clauses]
    
    @staticmethod
    def getEdgeLiteralDictsFromNodeDict(nodeDict):
        # A nodeDict is a dictionary where each key is a vertex label,
        # nodeDict[vertex] should be a tuple of the vertex labels of each adjacent vertex.
        # Returns 2 dictionaries: edgeToLiteral and literalToEdge.
        # edgeToLiteral:  Each key is a tuple (vertex label A, vertex label B) in sorted order. Each value is a unique literal.
        # literalToEdge:  Each key is a unique literal. Each value is a tuple (vertex label A, vertex label B) in sorted order.
        literalCount = 1
        edges = set()
        edgeToLiteral = dict()
        literalToEdge = dict()
        for node, neighbors in nodeDict.items():
            for neighbor in neighbors:
                edge = tuple(sorted((node, neighbor)))
                edges.add(edge)
        for edge in edges:
            edgeToLiteral[edge] = literalCount
            literalToEdge[literalCount] = edge
            literalCount += 1
        return (edgeToLiteral, literalToEdge)
    
    @staticmethod
    def getNodeLiteralDictsFromNodeDict(nodeDict):
        # A nodeDict is a dictionary where each key is a vertex label,
        # nodeDict[vertex] should be a tuple of the vertex labels of each adjacent vertex.
        # Returns 2 dictionaries: nodeToLiteral and literalToNode.
        # nodeToLiteral:  Each key is a vertex label. Each value is a unique literal.
        # literalToNode:  Each key is a unique literal. Each value is a vertex label.
        literalCount = 1
        nodeToLiteral = dict()
        literalToNode = dict()
        for node in nodeDict.keys():
            nodeToLiteral[node] = literalCount
            literalToNode[literalCount] = node
            literalCount += 1
        return (nodeToLiteral, literalToNode)
                

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

    # Given a set of literals, this produces a set of clauses that is
    # only SAT when exactly one literal is true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    @staticmethod
    def exactlyOne(inLiterals, startLiteral = None):
        # S=1(y_1,...y_p) = S<=1(y_1,...y_p) /\ (y_1 \/ y_2) \/ ... \/ y_p)
        leOne = SATUtils.oneOrLess(inLiterals, startLiteral)
        leOne[0].append(inLiterals)
        return leOne

    # Given a set of literals, this produces a set of clauses that is
    # only SAT when one or less literals are true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    @staticmethod
    def oneOrLess(inLiterals, startLiteral = None):
        clauses = []
        if startLiteral == None:
            startLiteral = max([abs(x) for x in inLiterals]) + 1
        if len(inLiterals) <= 1: # in hindsight, this case isn't needed
            # A set of one literals always has 1 or less true literals
            # so an empty set of clauses is returned (Always SAT)
            return ([], inLiterals[0])
        if len(inLiterals) <= 4:
            # for each pair of inLiterals, ensure no two are True
            for k in range(2, len(inLiterals)+1):
                for j in range(1, k):
                    clauses.append([-inLiterals[j-1], -inLiterals[k-1]])
            return (clauses, max([abs(x) for x in inLiterals]))
        else:
            # Recursively defined S(y_1,...,y_p)=
            # S(y_1,y_2,y_3,t) /\ S(^t,y_4,...y_p)

            # lhs = S(y_1,y_2,y_3,t)
            lhs = SATUtils.oneOrLess(inLiterals[0:3] + [startLiteral])
            # rhs = S(^t,y_4,...y_p)
            rhs = SATUtils.oneOrLess([-startLiteral] + inLiterals[3:])
            # return lhs /\ rhs
            return (lhs[0] + rhs[0], rhs[1])

    # Given a set of literals and r, this produces a set of clauses that is
    # only SAT when exactly r terms are true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    # IMPORTANT! After some additional testing I don't think this works
    # I don't think it's valid to mix inLiterals from atLeast and atMost
    # because they aren't actually the same.
    @staticmethod
    def exactlyR(inLiterals, r, startLiteral = None):
        # raise NotImplementedError()
        geResult = SATUtils.atLeast(inLiterals, r, startLiteral)
        clauses = geResult[0]
        ltResult = SATUtils.atMost(inLiterals, r, geResult[1] + 1)
        clauses = clauses + ltResult[0]
        return (clauses, ltResult[1])

    # Given a set of literals and r, this produces a set of clauses that is
    # only SAT when at least r terms are true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    @staticmethod
    def atLeast(inLiterals, r, startLiteral = None):
        inLiterals = [-x for x in inLiterals]
        return SATUtils.atMost(inLiterals, len(inLiterals) - r, startLiteral)

    # Given a set of literals and r, this produces a set of clauses that is
    # only SAT when at most r terms are true. Auxiliary literals start at
    # 1+max(map(abs,literals)) or at the specified startLiteral
    @staticmethod
    def atMost(inLiterals, r, startLiteral = None):
        if startLiteral == None:
            startLiteral = max([abs(x) for x in inLiterals]) + 1
        if r == 0:
            return ([[-x] for x in inLiterals], max([abs(x) for x in inLiterals]))
        elif r == 1:
            return SATUtils.oneOrLess(inLiterals, startLiteral)
        elif r == len(inLiterals):
            return ([[x] for x in inLiterals], max([abs(x) for x in inLiterals]))
        elif r == len(inLiterals) - 1:
            return ([[-x for x in inLiterals]], max([abs(x) for x in inLiterals]))
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

    # Given a set of a set of clauses and r, this produces a set of clauses
    # that is only SAT when at least r sets of clauses (from the original set of sets)
    # is SAT. Auxiliary literals start at 1+max(map(abs,literals)) or at the specified
    # startLiteral
    @staticmethod
    def atLeastRsub(groups, r, startLiteral = None):
        return SATUtils.assertRsub(groups, r, SATUtils.atLeast, startLiteral)

    # Given a set of a set of clauses and r, this produces a set of clauses
    # that is only SAT when at most r sets of clauses (from the original set of sets)
    # is SAT. Auxiliary literals start at 1+max(map(abs,literals)) or at the specified
    # startLiteral
    @staticmethod
    def atMostRsub(groups, r, startLiteral = None):
        return SATUtils.assertRsub(groups, r, SATUtils.atMost, startLiteral)

    # Given a set of a set of clauses and r, this produces a set of clauses
    # that is only SAT when at most r sets of clauses (from the original set of sets)
    # is SAT. Auxiliary literals start at 1+max(map(abs,literals)) or at the specified
    # startLiteral
    @staticmethod
    def exactlyRsub(groups, r, startLiteral = None):
        return SATUtils.assertRsub(groups, r, SATUtils.exactlyR, startLiteral)


    # Given a set of a set of clauses and r, this produces a set of clauses
    # that is only SAT when r sets of clauses (from the original set of sets)
    # satisfy the given constraint. Auxiliary literals start at 1+max(map(abs,literals)) or at the specified
    # startLiteral
    @staticmethod
    def assertRsub(groups, r, constraint, startLiteral = None):
        if startLiteral == None:
            startLiteral = max([max([max([abs(literal) for literal in clause]) for clause in group]) for group in groups]) + 1
        # create a new literal for each group passed in
        newVars = range(startLiteral, startLiteral + len(groups))
        # add each negated literal to its associated group
        groups = [[x + [-newVars[i]] for x in group] for i, group in enumerate(groups)]
        # assert r of those groups are satisfy the constraint
        geResult = constraint(newVars, r)
        # print(geResult[0])
        # flatten the groups into one set of clauses then add the new clauses
        return (reduce((lambda x, y: x + y), groups) + geResult[0], geResult[1], geResult[0])

    @staticmethod
    def waerden(j, k, n):
        clauses = []
        # positive literals
        d=1
        keepGoing = True
        while keepGoing:
            keepGoing = False
            for i in range(1, n - (j - 1) * d + 1):
                clauses.append([i + j_idx * d for j_idx in range(j)])
                keepGoing = True
            d += 1

        # negative literals
        d=1
        keepGoing = True
        while keepGoing:
            keepGoing = False
            for i in range(1, n - (k - 1) * d + 1):
                clauses.append([-(i + k_idx*d) for k_idx in range(k)])
                keepGoing = True
            d += 1
        return clauses

    @staticmethod
    def W(j, k):
        n = 0
        while True:
            if pycosat.solve(SATUtils.waerden(j,k,n)) == 'UNSAT':
                return n
            n += 1

class Tseytin:
    # C = A & B
    @staticmethod
    def AND(A, B, startLiteral = None):
        if startLiteral == None:
            startLiteral = max(A, B) + 1
        C = startLiteral
        return ([[-A, -B, C], [A, -C], [B, -C]], C)

    # C = ~(A & B)
    @staticmethod
    def NAND(A, B, startLiteral = None):
        if startLiteral == None:
            startLiteral = max(A, B) + 1
        C = startLiteral
        return ([[-A, -B, -C], [A, C], [B, C]], C)

    # C = A | B
    @staticmethod
    def OR(A, B, startLiteral = None):
        if startLiteral == None:
            startLiteral = max(A, B) + 1
        C = startLiteral
        return ([[A, B, -C], [-A, C], [-B, C]], C)

    # C = A -> B
    # C = ~A | B
    @staticmethod
    def IMPLIES(A, B, startLiteral = None):
        if startLiteral == None:
            startLiteral = max(A, B) + 1
        C = startLiteral
        return ([[-A, B, -C], [A, C], [-B, C]], C)

    # C = ~(A | B)
    @staticmethod
    def NOR(A, B, startLiteral = None):
        if startLiteral == None:
            startLiteral = max(A, B) + 1
        C = startLiteral
        return ([[A, B, C], [-A, -C], [-B, -C]], C)

    # C = ~A
    @staticmethod
    def NOT(A, startLiteral = None):
        if startLiteral == None:
            startLiteral = A + 1
        C = startLiteral
        return ([[-A, -C], [A, C]], C)

    # C = A ^ B
    @staticmethod
    def XOR(A, B, startLiteral = None):
        if startLiteral == None:
            startLiteral = max(A, B) + 1
        C = startLiteral
        return ([[-A, -B, -C], [A, B, -C], [A, -B, C], [-A, B, C]], C)

    # C = ~(A ^ B)
    @staticmethod
    def XNOR(A, B, startLiteral = None):
        if startLiteral == None:
            startLiteral = max(A, B) + 1
        C = startLiteral
        return ([[A, -B, -C], [-A, B, -C], [-A, -B, C], [A, B, C]], C)

def tst2():
    cnf = CNF([[1, 2], [3, 4]])
    print(cnf.rawCNF())
    DSAT(cnf).printCNF()

def tst():
    clause1 = Clause([Literal(1, 'abc'), Literal(3, 'a'), Literal(65, '3h'), Literal(2, 'sadfas')],'first', 'important')
    clause2 = Clause([Literal(11, 'abc'), Literal(-33, 'a'), Literal(635, '3h'), Literal(42, 'sadfas')],'second', 'important')
    clause3 = Clause([Literal(-1, '3abc'), Literal(4, '4a'), Literal(65, '344h'), Literal(2, '123sadfas')],'third', 'not important')
    cnf = CNF([clause1, clause2, clause3])
    dSAT = DSAT(cnf)
    #pp.pprint(dSAT.rawCNF())
    print('------------------------------------------')
    # dSAT.viewClausesAfterPartialAssignment([-2, -4, -65])
    dSAT.printCNF()
    print('------------------------------------------')
    dSAT.cnf.mergeWithRaw([[1,3,3, 65, 2, 2]])
    dSAT.printCNF()

if __name__ == '__main__':
    tst2()