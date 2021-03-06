from McGregor import McGregor
import random as rand
from SATSolver import SATSolver
from SATUtils import SATUtils
from GraphColoring import GraphColoring
from LogicFormula import *
import pycosat
import math
import numpy as np
import pprint as pp

class Experiments:
    def __init__(self):
        self.literalMapping = dict()
        self.reverseLiteralMapping = dict()
        self.auxLiteral = 1
        self.clauses = []

    def assertNoLoops(self, height, width):
        symbolDict = dict()
        for i in range(height * 2 - 1):
            for j in range(width * 2 - 1):
                # junctions
                if not ((i%4 == 1 or i%4 ==3) and (j%4 == 1 or j%4 ==3)) and (i+j)%2 == 0:
                    if '+' not in symbolDict:
                        symbolDict['+'] = [(i, j)]
                    else:
                        symbolDict['+'].append((i, j))

                # Lengthwise edges
                if (i+j) % 2 != 0 and j % 2 == 0:
                    if '|' not in symbolDict:
                        symbolDict['|'] = [(i, j)]
                    else:
                        symbolDict['|'].append((i, j))

                # crosswise edges
                if (i+j) % 2 != 0 and j % 2 != 0:
                    if '-' not in symbolDict:
                        symbolDict['-'] = [(i, j)]
                    else:
                        symbolDict['-'].append((i, j))

                # centers
                if (i%4 == 1 or i%4 ==3) and (j%4 == 1 or j%4 ==3):
                    if 'b' not in symbolDict:
                        symbolDict['b'] = [(i, j)]
                    else:
                        symbolDict['b'].append((i, j))


        nodeDict = dict()

        # At each junction in the puzzle, make sure all surrounding edges form a k-clique
        for junction in symbolDict['+']:
            nodesInClique = [x for x in symbolDict['-'] + symbolDict['|'] \
                             if (abs(x[0]-junction[0]) == 1 and abs(x[1]-junction[1]) == 0) \
                             or (abs(x[0]-junction[0]) == 0 and abs(x[1]-junction[1]) == 1)]
            for i, a in enumerate(nodesInClique):
                for b in nodesInClique[i+1:]:
                    if a != b:
                        if a not in nodeDict:
                            nodeDict[a] = [b]
                        else:
                            nodeDict[a].append(b)
                        if b not in nodeDict:
                            nodeDict[b] = [a]
                        else:
                            nodeDict[b].append(a)

        # define new external node that touches all centers on the outer ring
        symbolDict['b'].append((-1, -1))
        nodeDict[(-1, -1)] = []
        for edge in symbolDict['|'] + symbolDict['-']:
            if edge[0] == 1 or edge[0] == 2*(height-1)-1 or edge[1] == 1 or edge[1] == 2*(width-1)-1:
                nodeDict[(-1, -1)].append(edge)
                nodeDict[edge].append((-1, -1))

        # for each blank square, list each surrounding edge
        blankEdgeDict = dict()
        for blank in symbolDict['b']:
            blankEdgeDict[blank] = []
        for edge in symbolDict['|'] + symbolDict['-']:
            if (edge[0] - 1, edge[1]) in blankEdgeDict:
                blankEdgeDict[(edge[0]-1, edge[1])].append(edge)
            if (edge[0], edge[1] - 1) in blankEdgeDict:
                blankEdgeDict[(edge[0], edge[1] - 1)].append(edge)
            if (edge[0] + 1, edge[1]) in blankEdgeDict:
                blankEdgeDict[(edge[0] + 1, edge[1])].append(edge)
            if (edge[0], edge[1] + 1) in blankEdgeDict:
                blankEdgeDict[(edge[0], edge[1] + 1)].append(edge)

        # for the one encapsulating blank square, add those edges
        for edge in symbolDict['|'] + symbolDict['-']:
            if edge[0] == 0 or edge[0] == 2*(height-1) or edge[1] == 0 or edge[1] == 2*(width-1):
                blankEdgeDict[(-1, -1)].append(edge)
        print(blankEdgeDict)


        self.symbolDict = symbolDict
        self.nodeDict = nodeDict
        pp.pprint(symbolDict)
        pp.pprint(nodeDict)

        Experiments.printGrid(height, width, symbolDict)


        # one literal for each edge
        for edge in symbolDict['|'] + symbolDict['-']:
            self.updateLiteralMapping(edge)

        # one literal for each blank square
        for edge in symbolDict['b']:
            self.updateLiteralMapping(tuple(['b'] + list(edge)))

        # one bonus literal that acts like a blank square touching every other square on the perimeter
        self.updateLiteralMapping((-1, -1))

        print(self.literalMapping)
        print(self.reverseLiteralMapping)


        # Assert adjacent blank spots have the same color if the edge is false
        blankSets = dict([(k, set(v)) for k, v in blankEdgeDict.items()])
        # print(blankSets)
        for bi in list(blankSets.keys())[:-1]:
            for bj in list(blankSets.keys())[1:]:
                sharedEdges = blankSets[bi].intersection(blankSets[bj])
                for edge in sharedEdges:
                    # this is an edge that borders 2 blank squares bi and bj
                    self.clauses.append([-self.literalMapping[tuple(['b'] + list(bi))], self.literalMapping[edge], self.literalMapping[tuple(['b'] + list(bj))]])

        # try to make one square a different color than the rest
        firstBlank = list(blankSets.keys())[0]
        leResult = SATUtils.atMostRsub([self.clauses + \
                             [[self.literalMapping[tuple(['b'] + list(bi))]], [-self.literalMapping[tuple(['b'] + list(x))]]] \
                             for x in list(blankSets.keys())[1:]], \
                            0, self.auxLiteral)
        # pp.pprint([self.literalMapping[tuple(['b'] + list(firstBlank))]] + [self.literalMapping[tuple(['b'] + list(x))] for x in list(blankSets.keys())[1:]])
        # self.clauses.append([self.literalMapping[tuple(['b'] + list(firstBlank))]])
        # self.clauses.append([-self.literalMapping[tuple(['b'] + list(x))] for x in list(blankSets.keys())[1:]])

        # pp.pprint(self.clauses)
        # pp.pprint(leResult)
        self.clauses = leResult[0]

    @staticmethod
    def printGrid(height, width, symbolDict):
        for i in range(height * 2 - 1):
            line = ''
            for j in range(width * 2 - 1):
                for symbol in ['+', '-', '|', 'b']:
                    if (i,j) in symbolDict[symbol]:
                        line += symbol
            print(line)

    def updateLiteralMapping(self, newSymbol):
        if newSymbol not in self.literalMapping:
            self.literalMapping[newSymbol] = self.auxLiteral
            self.reverseLiteralMapping[self.auxLiteral] = newSymbol
            self.auxLiteral += 1

    def getSymbol(self, literal):
        if abs(literal) not in self.reverseLiteralMapping:
            if abs(literal) <= self.auxLiteral:
                return (1 if literal > 0 else -1, ('aux', literal))
            else:
                raise Exception('Unknown literal (SAT)')
        else:
            tmp = self.reverseLiteralMapping[abs(literal)]
            if literal > 0:
                return (1, tmp)
            else:
                return (-1, tmp)

    def getLiteral(self, symbol):
        polarity = symbol[0]
        name = symbol[1][0]
        auxLiteral = symbol[1][1]
        if symbol[1] not in self.literalMapping:
            raise Exception('Unknown symbol (SAT)')
        else:
            if name == 'aux':
                return auxLiteral*polarity
            tmp = self.literalMapping[symbol[1]]
            return tmp*polarity

    @staticmethod
    def detectAcyclicGridsWithGraphColoring():
        exprmnts = Experiments()
        exprmnts.assertNoLoops(3, 3)
        pp.pprint(list(pycosat.solve(exprmnts.clauses)))

    @staticmethod
    def testWaerden():
        # clauses = SATUtils.waerden(3,3,8)
        # pp.pprint(clauses)
        for k in range(3, 20):
            print(SATUtils.W(3,k))

    @staticmethod
    def testGraphGeneration():
        pp.pprint(GraphColoring.P(5,zeroIndexed=True))
        pp.pprint(GraphColoring.P(5,zeroIndexed=False))
        print('')
        pp.pprint(GraphColoring.C(5,zeroIndexed=True))
        pp.pprint(GraphColoring.C(5,zeroIndexed=False))
        print('')
        pp.pprint(GraphColoring.K(5,zeroIndexed=True))
        pp.pprint(GraphColoring.K(5,zeroIndexed=False))
        print('')
        pp.pprint(GraphColoring.invert(GraphColoring.C(5)))
        pp.pprint(GraphColoring.invert(GraphColoring.P(5)))
        pp.pprint(GraphColoring.invert(GraphColoring.K(5)))
        # pp.pprint(GraphColoring.invert(GraphColoring.strongProduct(GraphColoring.P(5), GraphColoring.P(5))))

    @staticmethod
    def testGraphOperations():
        A = GraphColoring.P(3)
        B = GraphColoring.P(3)
        cart = GraphColoring.cartesianProduct(A,B)
        tens = GraphColoring.tensorProduct(A,B)
        strong = GraphColoring.strongProduct(A, B)
        strong2 = GraphColoring.merged(GraphColoring.cartesianProduct(A,B),GraphColoring.tensorProduct(A,B))
        tmp = 0

    @staticmethod
    def testAlgoA():
        F = [[1, -2], [2, 3], [-1, -3], [-1, -2, 3]]
        G = F + [[1, 2, -3]]
        H = [[rand.choice([-1, 1])*rand.randint(1, 100) for _ in range(3)] for _ in range(200)]
        solver = SATSolver(McGregor(4, 4).clauses, SATSolver.Algorithm_A)
        # solver = SATSolver(H, SATSolver.Algorithm_A)
        solver.compare()

    @staticmethod
    def singleLoopGraph():
        F = GraphColoring.C(5)
        G = GraphColoring.C(4)
        print(F)
        print(G)
        Gp = dict()
        delta = 5
        for k, v in G.items():
            Gp[k+delta] = tuple([x + delta for x in v])
        F.update(Gp)
        print(F)
        [edgeToLiteral, literalToEdge] = SATUtils.getEdgeLiteralDictsFromNodeDict(F)
        [nodeToLiteral, literalToNode] = SATUtils.getNodeLiteralDictsFromNodeDict(F)
        print("edgeToLiteral:", edgeToLiteral)
        print("literalToEdge:", literalToEdge)
        print("nodeToLiteral:", nodeToLiteral)
        print("literalToNode:", literalToNode)

    @staticmethod
    def TseytinCustom():
        a = Wire()
        b = Wire()
        cin = Wire()
        sum = Wire()
        cout = Wire()
        fa1 = GateCustom()
        fa1.FullAdder(a, b, cin, sum, cout)
        logicForm = LogicFormula([a, b, cin])
        logicForm.getTseytinCNF()
        cnfFormula = logicForm.cnfForm.rawCNF()
        for solution in pycosat.itersolve(cnfFormula):
            print(solution)

    @staticmethod
    def TseytinCustomLargeOR():
        a = Wire()
        b = Wire()
        c = Wire()
        d = Wire()
        out = Wire()
        fa1 = GateCustom()
        fa1.ORwide([a, b, c, d], out)
        logicForm = LogicFormula([a, b, c, d])
        logicForm.getTseytinCNF()
        cnfFormula = logicForm.cnfForm.rawCNF()
        for solution in pycosat.itersolve(cnfFormula):
            print(solution)

    @staticmethod
    def TseytinSimple():
        a = Wire()
        b = Wire()
        andGate = Gate2(LogicStructure.XNOR, a, b)
        c = andGate.output
        # notGate = Gate1(LogicGate.NOT, c)
        # d = notGate.output
        logicForm = LogicFormula([a,b])
        logicForm.getTseytinCNF()
        cnfFormula = logicForm.cnfForm.rawCNF()
        for solution in pycosat.itersolve(cnfFormula):
            print(solution)

    @staticmethod
    def TseytinComparator():
        a0 = Wire()
        b0 = Wire()
        a1 = Wire()
        b1 = Wire()
        a2 = Wire()
        b2 = Wire()
        lt = Wire()
        eq = Wire()
        gt = Wire()
        comparator = GateCustom()
        comparator.ComparatorNBit([a0, a1, a2], [b0, b1, b2], lt, eq, gt)
        logicForm = LogicFormula([a0, a1, a2, b0, b1, b2])
        logicForm.getTseytinCNF()
        cnfFormula = logicForm.cnfForm.rawCNF()
        for solution in pycosat.itersolve(cnfFormula):
            print(solution)
        print('')

    @staticmethod
    def TseytinSADD():
        a = [Wire() for _ in range(8)]
        sadd = GateCustom()
        sadd.SidewaysAdd(a)
        logicForm = LogicFormula(a)
        logicForm.getTseytinCNF()
        cnfFormula = logicForm.cnfForm.rawCNF()
        for solution in pycosat.itersolve(cnfFormula):
            print(solution)
        print('')

    @staticmethod
    def TseytinEquals():
        aAct = [Wire() for _ in range(16)]
        aExp = [Wire() for _ in range(16)]
        aExp[0].constant = True
        aExp[1].constant = True
        aExp[2].constant = False
        aExp[3].constant = True
        aExp[4].constant = False
        aExp[5].constant = False
        aExp[6].constant = False
        aExp[7].constant = False
        aExp[8].constant = True
        aExp[9].constant = True
        aExp[10].constant = False
        aExp[11].constant = True
        aExp[12].constant = False
        aExp[13].constant = False
        aExp[14].constant = False
        aExp[15].constant = False
        isEq = Wire()
        isEq.constant = True
        eq = GateCustom()
        eq.EqualsExpected(aAct, aExp, isEq)
        logicForm = LogicFormula(aAct + aExp)
        logicForm.getTseytinCNF()
        cnfFormula = logicForm.cnfForm.rawCNF()
        for solution in pycosat.itersolve(cnfFormula):
            print(solution)
        print('')

    @staticmethod
    def TseytinLIFE():
        prevTiles = [Wire() for _ in range(9)]
        # prevTiles[0].constant = False
        # prevTiles[1].constant = True
        # prevTiles[2].constant = True
        # prevTiles[3].constant = True

        prevTiles[4].constant = True

        # prevTiles[5].constant = False
        # prevTiles[6].constant = False
        # prevTiles[7].constant = False
        # prevTiles[8].constant = False
        nextTile = Wire()
        nextTile.constant = True
        life = GateCustom()
        life.LIFE_nextState(prevTiles, nextTile)
        logicForm = LogicFormula(prevTiles)
        assertedInputWires = set(logicForm.assertedInputWires)
        detectedInputWires = set(logicForm.detectedInputWires)
        constantWires = set(logicForm.constantWires)
        freeInputs = set(logicForm.freeInputs)
        assert detectedInputWires.difference(constantWires) == freeInputs, "The set of input wires minus all wires assigned constant values should be the remaining free inputs"
        cnfFormula = sorted(logicForm.cnfForm.rawCNF(),key=lambda x: [len(x), [abs(y) for y in x]])
        cnt = 0
        for solution in pycosat.itersolve(cnfFormula):
            # print(solution)
            cnt += 1
        print(cnt)
        print(SATUtils.nCr(8,2) + SATUtils.nCr(8,3))

    @staticmethod
    def Tseytin_RS_NOR_Latch():
        r = Wire()
        s = Wire()
        q = Wire()
        qn = Wire()
        norGate1 = Gate2(LogicStructure.NOR, r, qn, q)
        norGate2 = Gate2(LogicStructure.NOR, s, q, qn)
        logicForm = LogicFormula([r,s])
        logicForm.getTseytinCNF()
        cnfFormula = logicForm.cnfForm.rawCNF()
        for solution in pycosat.itersolve(cnfFormula):
            print(solution)
        # WOW! This is so cool
        # I could check that a formula is combinational by seeing if there exists a solution where two inputs
        # match but all outputs don't match
        #
        # [-1, -2, -3, 4]       neither Set nor Reset asserted, q can be either true or false
        # [-1, -2, 3, -4]       same as above!
        # [-1, 2, 3, -4]        Set asserted, therefore q must be true
        # [1, 2, -3, -4]        both Set and Reset asserted, neither q not qn true
        # [1, -2, -3, 4]        Reset asserted, therefore qn must be true

    @staticmethod
    def Tseytin_Test_Constants():
        A = Wire()
        B = Wire()
        C = Wire()
        D = Wire()
        E = Wire()
        F = Wire()
        out = Wire()
        E.constant = True
        F.constant = False
        Gate2(LogicStructure.AND, A, B, C)
        Gate2(LogicStructure.AND, E, F, D)
        Gate2(LogicStructure.AND, C, D, out)
        logicForm = LogicFormula([A, B])
        assertedInputWires = set(logicForm.assertedInputWires)
        detectedInputWires = set(logicForm.detectedInputWires)
        constantWires = set(logicForm.constantWires)
        freeInputs = set(logicForm.freeInputs)
        assert detectedInputWires.difference(constantWires) == freeInputs, "The set of input wires minus all wires assigned constant values should be the remaining free inputs"
        cnfFormula = sorted(logicForm.cnfForm.rawCNF())
        cnt = 0
        for solution in pycosat.itersolve(cnfFormula):
            # print(solution)
            cnt += 1
        print(cnt)


if __name__ == "__main__":
    Experiments.TseytinLIFE()