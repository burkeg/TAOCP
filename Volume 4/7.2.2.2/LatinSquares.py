import pycosat
import itertools
import math
import numpy as np
import pprint as pp
import sys
import collections
from SATUtils import SATUtils, CNF, Clause, Literal, DSAT, Tseytin, LiteralAllocator

class LatinSquare:
    def __init__(self, n, symbols):
        self.n = n
        self.symbols = symbols
        self.board = None
        self.la = LiteralAllocator()
        self.literal2board = dict()
        self.board2literal = dict()
        self.cnf = CNF()
        self.InitSquare()
        self.Assert()

    def InitSquare(self):
        self.board = []
        for row in range(self.n):
            cols = []
            for col in range(self.n):
                symbols = []
                for symbol in range(self.symbols):
                    symbolVals = []
                    for symbolVal in range(self.n):
                        literal = self.la.getLiteral()
                        self.board2literal[(row, col, symbol, symbolVal)] = literal
                        symbolVals.append(literal)
                    symbols.append(symbolVals)
                cols.append(symbols)
            self.board.append(cols)


        #                                     number of possible symbol values    | how many symbol types |  columns           |            rows
        # self.board = [[[[self.la.getLiteral() for _ in range(self.n)] for _ in range(self.symbols)] for _ in range(self.n)] for _ in range(self.n)]
        pp.pprint(self.board)

    def Assert(self):
        # Asserts that for each symbol, it doesn't share a row or column with the same symbol
        for symbol in range(self.symbols):
            for row in range(self.n):
                for col in range(self.n):
                    for i in range(self.n):
                        for j in range(self.n):
                            if (row == i) ^ (col == j):
                                for symbolVal in range(self.n):
                                    self.cnf.addClause(
                                        [-self.board[row][col][symbol][symbolVal],
                                         -self.board[i][j][symbol][symbolVal]])

        # Assert that each symbol has a single value assigned
        for symbol in range(self.symbols):
            for row in range(self.n):
                for col in range(self.n):
                    self.cnf.mergeWithRaw(SATUtils.exactlyOne(self.board[row][col][symbol], forceInefficient=True)[0])


        # For each pair of symbols, they never appear twice
        for symbolA, symbolB in itertools.combinations(range(self.symbols), 2):
            for symbolValA in range(self.n):
                for symbolValB in range(self.n):
                    # get pairs of literals and AND them together. That value must be
                    # true exactly 1 time for each pairing of symbol types.
                    impliedLiterals = []
                    for row in range(self.n):
                        for col in range(self.n):
                            clauses, C = Tseytin.AND(self.board[row][col][symbolA][symbolValA],
                                        self.board[row][col][symbolB][symbolValB],
                                        self.la.getLiteral())
                            impliedLiterals.append(C)
                            self.cnf.mergeWithRaw(clauses)
                    self.cnf.mergeWithRaw(SATUtils.atLeast(impliedLiterals, 1)[0])


        # pp.pprint(sorted(self.cnf.rawCNF(), key=lambda x: [abs(_) for _ in x]))

    def Solve(self):
        finalVals = pycosat.solve(self.cnf.rawCNF())
        rows = []
        for row in range(self.n):
            cols = []
            for col in range(self.n):
                symbols = []
                for symbol in range(self.symbols):
                    for symbolVal in range(self.n):
                        val = self.board2literal[(row, col, symbol, symbolVal)]
                        if val in finalVals:
                            symbols.append(symbolVal)
                            break
                cols.append(symbols)
            rows.append(cols)
        pp.pprint(rows)



def Solve():
    LatinSquare(4, 2).Solve()

if __name__ == '__main__':
    Solve()