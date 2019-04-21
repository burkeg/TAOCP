import sys
import pprint as pp
import copy
import operator as op
import pycosat
from functools import reduce
import itertools
from SATUtils import SATUtils, CNF, Clause, Literal, DSAT, Tseytin

class Circuit:
    def __init__(self):
        self.terms=[]

class Term:
    def __init__(self, ID, inputs=(), funct=None):
        self.inputs=inputs
        self.funct=funct
        self.ID = ID

    def eval(self):
        if self.funct == None:
            raise Exception("Tried to evaluate an input as a gate's output")
        return self.funct(*self.inputs)

class Multiplier(Circuit):
    def __init__(self, m, n):
        super(Multiplier, self).__init__()
        self.m=m
        self.n=n
        self.bins = [[] for _ in range(m+n)]

    def createInitialTerms(self):
        terms = []
        # m input bits x
        for m in range(1,self.m+1):
            terms.append(Term(('x', m)))

        # n input bits y
        for n in range(1,self.n+1):
            terms.append(Term(('y', n)))

        # m*n intermediate bits i
        for m in range(1,self.m+1):
            mTerm = Term(('x', m))
            terms.append(mTerm)
            nFirst = True
            for n in range(1,self.n+1):
                nTerm = Term(('y', n))

                terms.append(Term(('i', m, n),
                                  [mTerm, nTerm],
                                  lambda x, y: Tseytin.conjSym(x.ID, y.ID)))
                if nFirst:
                    terms.append(nTerm)
                    nFirst=False

        # m+n product bits z
        for z in range(1, self.m+self.n+1):
            terms.append(Term(('z', z)))

        self.terms = terms

    def createBins(self):
        bins = [[] for _ in range(self.m+self.n)]
        rCount = 0
        for interBit in self.terms:
            if interBit.ID[0] == 'i':
                # bin index is the sum of the intermediate bit's indices (0-indexed)
                bins[interBit.ID[1]+interBit.ID[2]-2].append(interBit)
        pp.pprint(bins)