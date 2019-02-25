import sys
import operator as op
from functools import reduce

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
    # IMPORTANT! After some additional testing I don't think this works
    # I don't think it's valid to mix inLiterals from atLeast and atMost
    # because they aren't actually the same.
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