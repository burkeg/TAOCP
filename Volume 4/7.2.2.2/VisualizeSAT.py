import pycosat
import math
import numpy as np
import pprint as pp
class Visualizer:
    def __init__(self, literals):
        self.literals = dict()
        if len(set([abs(x) for x in literals])) != len(literals):
            raise Exception("")
        for literal in literals:
            self.literals[abs(literal)] = None #True if literal > 0 else False

    def __repr__(self):
        return "Visualizer()"

    def __str__(self):
        return str(self.literals)


    def assignLiteral(self, literal):
        # print('Assigning ' + str(literal))
        self.literals[abs(literal)] = True if literal > 0 else False
        # print(self)

    def unassignLiteral(self, literal):
        # print('Unassigning ' + str(literal))
        self.literals[abs(literal)] = None
        # print(self)


if __name__ == '__main__':
    v = Visualizer([1, -2, 3, -4, -5])
    v.assignLiteral(7)
    v.unassignLiteral(3)
    print(v)