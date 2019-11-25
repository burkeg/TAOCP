from enum import Enum
from collections import deque
from SATUtils import CNF, Tseytin
class LogicStructure(Enum):
    AND = 0
    NAND = 1
    OR = 2
    NOR = 3
    NOT = 4
    XOR = 5
    XNOR = 6
    IMPLIES = 7
    CUSTOM = 8

class LogicFormula:
    def __init__(self, inputs, startLiteral=None, overwriteLiterals=True):
        self.inputs = inputs
        if overwriteLiterals:
            LogicFormula.assignVariables(inputs, startLiteral)
        self.usedLiterals = self.getAllUsedVariables(self.inputs)
        if startLiteral is None:
            startLiteral = max(self.usedLiterals) + 1
        self.cnfForm = None

    def getTseytinCNF(self):
        self.cnfForm = CNF()
        if len(self.inputs) == 0:
            return
        visited = set()
        componentQueue = deque(self.inputs)
        visited.add(componentQueue[0])
        while len(componentQueue) != 0:
            v = componentQueue.popleft()
            if isinstance(v,Wire):
                if v.variable is None:
                    raise Exception('All wire components must have a variable bound.')
                for gate in v.gatesIn:
                    if gate not in visited:
                        visited.add(gate)
                        componentQueue.append(gate)
            elif issubclass(type(v), Gate):
                if v.output not in visited:
                    visited.add(v.output)
                    componentQueue.append(v.output)
                    self.cnfForm.mergeWithRaw(self.getTseytinSingleGate(v))
            else:
                raise Exception("Logic structure should only contain Wires and Gates")

    def getTseytinSingleGate(self, gate):
        if not issubclass(type(gate), Gate):
            raise Exception("Must be of type gate")
        # If you manage to get here with inputs/outputs as None I'm impressed!
        if isinstance(gate, Gate2):
            varA = gate.inputA.variable
            varB = gate.inputB.variable
            varOut = gate.output.variable
            if gate.gateType == LogicStructure.AND:
                newClauses, _= Tseytin.AND(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicStructure.NAND:
                newClauses, _= Tseytin.NAND(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicStructure.OR:
                newClauses, _= Tseytin.OR(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicStructure.NOR:
                newClauses, _= Tseytin.NOR(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicStructure.XOR:
                newClauses, _= Tseytin.XOR(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicStructure.XNOR:
                newClauses, _= Tseytin.XNOR(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicStructure.IMPLIES:
                newClauses, _= Tseytin.IMPLIES(varA, varB, varOut)
                return newClauses
            else:
                raise Exception('Unknown gate')
        elif isinstance(gate, Gate1):
            varA = gate.inputA.variable
            varOut = gate.output.variable
            if gate.gateType == LogicStructure.NOT:
                newClauses, _= Tseytin.NOT(varA, varOut)
                return newClauses
            else:
                raise Exception('Unknown gate')
        elif isinstance(gate, GateCustom):
            raise Exception("Custum logic structures aren't always gates")

    def getAllUsedVariables(self, inputs):
        if len(inputs) == 0:
            return set()
        visited = set()
        componentQueue = deque(inputs)
        usedVariables = set()
        visited.add(componentQueue[0])
        while len(componentQueue) != 0:
            v = componentQueue.popleft()
            if isinstance(v,Wire):
                if v.variable is None:
                    raise Exception('All wire components must have a variable bound.')
                else:
                    usedVariables.add(v.variable)
                for gate in v.gatesIn:
                    if gate not in visited:
                        visited.add(gate)
                        componentQueue.append(gate)
            elif issubclass(type(v), Gate):
                if v.output not in visited:
                    visited.add(v.output)
                    componentQueue.append(v.output)
            else:
                raise Exception("Logic structure should only contain Wires and Gates")
        return usedVariables

    @staticmethod
    def assignVariables(inputs, startLiteral=None):
        if len(inputs) == 0:
            return
        if startLiteral is None:
            startLiteral = 1
        literalTracker = startLiteral
        visited = set()
        componentQueue = deque(inputs)
        visited.add(componentQueue[0])
        while len(componentQueue) != 0:
            v = componentQueue.popleft()
            if isinstance(v,Wire):
                v.variable = literalTracker
                literalTracker += 1
                for gate in v.gatesIn:
                    if gate not in visited:
                        visited.add(gate)
                        componentQueue.append(gate)
            elif issubclass(type(v), Gate):
                if v.output not in visited:
                    visited.add(v.output)
                    componentQueue.append(v.output)
            else:
                raise Exception("Logic structure should only contain Wires and Gates")
        return literalTracker-1

    # https://en.wikipedia.org/wiki/Tseytin_transformation
    @staticmethod
    def WikipediaExample():
        x1 = Wire()
        x2 = Wire()
        x3 = Wire()
        gate1 = Wire()
        not1 = Gate1(LogicStructure.NOT, x1, gate1)
        gate3_5 = Wire()
        not2 = Gate1(LogicStructure.NOT, x2, gate3_5)
        gate2 = Wire()
        and1 = Gate2(LogicStructure.AND, gate1, x2, gate2)
        gate4 = Wire()
        and2 = Gate2(LogicStructure.AND, x1, gate3_5, gate4)
        gate6 = Wire()
        and3 = Gate2(LogicStructure.AND, gate3_5, x3, gate6)
        gate7 = Wire()
        or1 = Gate2(LogicStructure.OR, gate2, gate4, gate7)
        gate8 = Wire()
        or2 = Gate2(LogicStructure.OR, gate7, gate6, gate8)
        y = gate8
        return [x1, x2, x3], [y]


class Gate:
    def __init__(self, gateType):
        self.gateType = gateType
        pass


class GateCustom(Gate):
    def __init__(self):
        super().__init__(LogicStructure.CUSTOM)

    def HalfAdder(self, A, B, S, Cout):
        # A = Wire()
        # B = Wire()
        # S = Wire()
        # Cout = Wire()
        xor1 = Gate2(LogicStructure.XOR, A, B, S)
        and1 = Gate2(LogicStructure.AND, A, B, Cout)
        self.inputs = [A, B]
        self.outputs = [S, Cout]

    def FullAdder(self, A, B, Cin, S, Cout):
        # A = Wire()
        # B = Wire()
        # Cin = Wire()
        # S = Wire()
        # Cout= Wire()
        sumAB = Wire()
        carryAB = Wire()
        HA1 = GateCustom()
        HA1.HalfAdder(A, B, sumAB, carryAB)
        carryABC = Wire()
        HA2 = GateCustom()
        HA1.HalfAdder(sumAB, Cin, S, carryABC)
        or2 = Gate2(LogicStructure.OR, carryAB, carryABC, Cout)

        self.inputs= [A, B, Cin]
        self.outputs= [S, Cout]

    def ANDwide(self, inputs, output):
        if len(inputs) == 0:
            raise Exception("0 input AND gate? Don't bother encoding! It's always True.")
        elif len(inputs) == 1:
            output = inputs[0]
            return
        elif len(inputs) == 2:
            # What're you doing? Just use a regular AND gate you dummy!
            Gate2(LogicStructure.AND, inputs[0], inputs[1], output)
            self.inputs = inputs
            self.outputs = [output]
            return
        andGate = Gate2(LogicStructure.AND, inputs[0], inputs[1])
        for i in range(2, len(inputs)-1):
            andGate = Gate2(LogicStructure.AND, andGate.output, inputs[i])
        Gate2(LogicStructure.AND, andGate.output, inputs[-1], output)
        self.inputs = inputs
        self.outputs = [output]

    def ORwide(self, inputs, output):
        if len(inputs) == 0:
            raise Exception("0 input AND gate? Don't bother encoding! It's always True.")
        elif len(inputs) == 1:
            output = inputs[0]
            return
        elif len(inputs) == 2:
            # What're you doing? Just use a regular OR gate you dummy!
            Gate2(LogicStructure.OR, inputs[0], inputs[1], output)
            self.inputs = inputs
            self.outputs = [output]
            return
        orGate = Gate2(LogicStructure.OR, inputs[0], inputs[1])
        for i in range(2, len(inputs)-1):
            orGate = Gate2(LogicStructure.OR, orGate.output, inputs[i])
        Gate2(LogicStructure.OR, orGate.output, inputs[-1], output)
        self.inputs = inputs
        self.outputs = [output]

    def Comparator1Bit(self, A, B, lt, eq, gt):
        not1 = Gate1(LogicStructure.NOT, A)
        not2 = Gate1(LogicStructure.NOT, B)
        and1 = Gate2(LogicStructure.AND, not1.output, B, lt)
        and2 = Gate2(LogicStructure.AND, not2.output, A, gt)
        nor1 = Gate2(LogicStructure.NOR, lt, gt, eq)
        self.inputs = [A, B]
        self.outputs = [lt, eq, gt]

    def ComparatorNBit(self, Abits, Bbits, lt, eq, gt):
        if len(Abits) != len(Bbits):
            raise Exception('A and B must have same number of bits!')
        if len(Abits) == 0:
            raise Exception("Cannot have a 0 bit Comparator")
        elif len(Abits) == 1:
            self.Comparator1Bit(Abits[0], Bbits[0], lt, eq, gt)
            return
        # Gets XORs of each inputs
        X = [Gate2(LogicStructure.XNOR, Ai, Bi).output for Ai, Bi in zip(Abits, Bbits)]
        eqAND = GateCustom()

        # If all XNORs of inputs are 1, then the two numbers are equal
        eqAND.ANDwide(X, eq)

        # To determine lt or gt, we need to get a chain of AND'd Xs in descending order first
        Xands = []
        lastXand = Gate2(LogicStructure.AND, X[len(Abits)-1], X[len(Abits)-2])
        Xands.append(lastXand.output)
        for i in reversed(range(1, len(Abits) - 2)):
            lastXand = Gate2(LogicStructure.AND, lastXand.output, X[i])
            Xands.append(lastXand.output)
        # Xands = [Xn-1, Xn-1&Xn-2, Xn-1&Xn-2&Xn-3, ..., Xn-1&Xn-2&...&X1]
        # len(Xands) = n-2

        # Now determine the values of the lt and gt outputs
        ltWires = []
        gtWires = []
        for i, (Ai, Bi) in enumerate(zip(Abits, Bbits)):
            # For lt, get ~Ai&Bi. gt: Ai&~Bi
            notA = Gate1(LogicStructure.NOT, Ai)
            notB = Gate1(LogicStructure.NOT, Bi)
            toBeAnd = []

            # Next, add the appropriate X's
            if i == len(Abits) - 1:
                # the highest bits don't have any X's
                pass
            elif i == len(Abits) - 2:
                # The 2nd highest bit only has Xn-1 and doesn't need to look at the cascaded ANDs or XORs list
                toBeAnd.append(X[len(Abits) - 1])
            else:
                toBeAnd.append(Xands[(len(Abits) - 3) - i])
                
            ltBigAnd = GateCustom()
            ltBigAndOut = Wire()
            ltBigAnd.ANDwide(toBeAnd + [notA.output, Bi], ltBigAndOut)
                
            gtBigAnd = GateCustom()
            gtBigAndOut = Wire()
            gtBigAnd.ANDwide(toBeAnd + [notB.output, Ai], gtBigAndOut)

            ltWires.append(ltBigAndOut)
            gtWires.append(gtBigAndOut)
            
        # Now or together all the previous results
        ltFinalGate = GateCustom()
        ltFinalGate.ORwide(ltWires, lt)
        gtFinalGate = GateCustom()
        gtFinalGate.ORwide(gtWires, gt)
            

        self.inputs = Abits + Bbits
        self.outputs = [lt, eq, gt]



class Gate2(Gate):
    def __init__(self, gateType, inputA=None, inputB=None, output=None):
        super().__init__(gateType)
        if inputA is None:
            self.inputA=Wire(gatesIn=self)
        else:
            self.inputA=inputA
            inputA.gatesIn.add(self)

        if inputB is None:
            self.inputB=Wire(gatesIn=self)
        else:
            self.inputB=inputB
            inputB.gatesIn.add(self)

        if output is None:
            self.output=Wire(gateOut=self)
        else:
            self.output=output
            output.gateOut = self


class Gate1(Gate):
    def __init__(self, gateType, inputA=None, output=None):
        super().__init__(gateType)
        if inputA is None:
            self.inputA=Wire(gatesIn=self)
        else:
            self.inputA=inputA
            inputA.gatesIn.add(self)

        if output is None:
            self.output=Wire(gateOut=self)
        else:
            self.output=output
            output.gateOut = self


class Wire:
    def __init__(self, gateOut=None, gatesIn=None, variable=None):
        self.variable = variable
        if gatesIn is None:
            gatesIn = set()
        self.gateOut = gateOut
            
        if isinstance(gatesIn, set):
            # If it's a set, accept it
            self.gatesIn = gatesIn
        elif isinstance(gatesIn, list):
            # If it's a list, first convert it to a set
            self.gatesIn = set(gatesIn)
        else:
            # Otherwise it's some other format, assume it's a single element of whatever format is passed in
            self.gatesIn = {gatesIn}


if __name__ == '__main__':
    theInputs, theOutputs = LogicFormula.WikipediaExample()
    formula = LogicFormula(theInputs, 1, overwriteLiterals=True)
    formula.getTseytinCNF()
    test = 0