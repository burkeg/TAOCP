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
        elif r == len(inLiterals):
            return ([[x for x in inLiterals]], max([abs(x) for x in inLiterals]))
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
        if startLiteral == None:
            startLiteral = max([max([max([abs(literal) for literal in clause]) for clause in group]) for group in groups]) + 1
        # create a new literal for each group passed in
        newVars = range(startLiteral, startLiteral + len(groups))
        # add each negated literal to its associated group
        groups = [[x + [-newVars[i]] for x in group] for i, group in enumerate(groups)]
        # assert at least r of those groups are SAT
        geResult = SATUtils.atLeast(newVars, r)
        # print(geResult[0])
        #flatten the groups into one set of clauses then add the new clauses
        return (reduce((lambda x, y: x + y), groups) + geResult[0], geResult[1], geResult[0])

