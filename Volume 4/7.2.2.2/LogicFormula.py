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
    IMPLIES = 6
    CUSTOM = 7

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
        andGate = Gate2(LogicStructure.AND, inputs[0], inputs[1])
        for i in range(2, len(inputs)):
            andGate = Gate2(LogicStructure.AND, andGate.output, inputs)
        output = andGate.output
        self.inputs = inputs
        self.outputs = [output]





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