import itertools
import math
import numpy as np
import pycosat
import pprint as pp
import time
from VisualizeSAT import Visualizer

class SATSolver:
    def __init__(self, cnf, strategy=pycosat.solve):
        self.cnf = cnf
        self.strategy = strategy

    @staticmethod
    def Algorithm_A(F):
        literals = set()
        for clause in F:
            literals.update(set([abs(x) for x in clause]))
        visualizer = Visualizer(list(literals))
        # returns clauses F conditioned on literal l
        def Fgivenl(F,l):
            return [[literal for literal in clause if literal != -l] for clause in F if l not in clause]

        def B(F):
            # If F = empty set, return empty set
            if len(F) == 0:
                return set()
            # otherwise if the empty clause is an element of F, return UNSAT
            elif [] in F:
                return 'UNSAT'
            # otherwise let l be a literal in F and set L <- B(F|l)
            else:
                l = F[0][0]
                FCondOnl = Fgivenl(F, l)
                visualizer.assignLiteral(l)
                L = B(FCondOnl)
            # If L != UNSAT, return L union l
            if L != 'UNSAT':
                L.add(l)
                return L
            # otherwise set L <- B(F|-l).
            else:
                visualizer.unassignLiteral(l)
                FCondOnnl = Fgivenl(F, -l)
                visualizer.assignLiteral(-l)
                L = B(FCondOnnl)
            # If L != UNSAT, return L union -l
            if L != 'UNSAT':
                L.add(-l)
                return L
            # otherwise return UNSAT
            else:
                visualizer.unassignLiteral(-l)
                return 'UNSAT'

        result = B(F)
        if result != 'UNSAT':
            result = sorted(list(result), key=abs)
        return result

    def solve(self):
        return self.strategy(self.cnf)

    def compare(self, alternateStrategy=pycosat.solve):
        t0 = time.time()
        answerA = alternateStrategy(self.cnf)
        t1 = time.time()
        print(alternateStrategy.__name__ + ': ' + str(t1-t0))
        t1 = time.time()
        answerB = self.solve()
        t2 = time.time()
        print(self.strategy.__name__ + ': ' + str(t2-t1))
        if t1-t0 == 0 or t2-t1 == 0:
            print('Too slow to tell.')
            return
        if t1-t0 > t2-t1:
            print(self.strategy.__name__ + ' ' + str((t1-t0) / (t2-t1)) + ' times faster.')
        else:
            print(alternateStrategy.__name__ + ' ' + str((t2-t1) / (t1-t0)) + ' times faster.')
