from enum import Enum
from collections import deque
from SATUtils import CNF, Tseytin
class LogicGate(Enum):
    AND = 0
    NAND = 1
    OR = 2
    NOR = 3
    NOT = 4
    XOR = 5
    IMPLIES = 6

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
            elif isinstance(v, Gate1) or isinstance(v, Gate2):
                if v.output not in visited:
                    visited.add(v.output)
                    componentQueue.append(v.output)
                    self.cnfForm.mergeWithRaw(self.getTseytinSingleGate(v))
            else:
                raise Exception("Logic structure should only contain Wires and Gates")

    def getTseytinSingleGate(self, gate):
        # If you manage to get here with inputs/outputs as None I'm impressed!
        if isinstance(gate, Gate2):
            varA = gate.inputA.variable
            varB = gate.inputB.variable
            varOut = gate.output.variable
            if gate.gateType == LogicGate.AND:
                newClauses, _= Tseytin.AND(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicGate.NAND:
                newClauses, _= Tseytin.NAND(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicGate.OR:
                newClauses, _= Tseytin.OR(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicGate.NOR:
                newClauses, _= Tseytin.NOR(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicGate.XOR:
                newClauses, _= Tseytin.XOR(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicGate.IMPLIES:
                newClauses, _= Tseytin.IMPLIES(varA, varB, varOut)
                return newClauses
            else:
                raise Exception('Unknown gate')
        if isinstance(gate, Gate1):
            varA = gate.inputA.variable
            varOut = gate.output.variable
            if gate.gateType == LogicGate.NOT:
                newClauses, _= Tseytin.NOT(varA, varOut)
                return newClauses
            else:
                raise Exception('Unknown gate')



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
            elif isinstance(v, Gate1) or isinstance(v, Gate2):
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
            elif isinstance(v, Gate1) or isinstance(v, Gate2):
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
        not1 = Gate1(LogicGate.NOT, x1, gate1)
        gate3_5 = Wire()
        not2 = Gate1(LogicGate.NOT, x2, gate3_5)
        gate2 = Wire()
        and1 = Gate2(LogicGate.AND, gate1, x2, gate2)
        gate4 = Wire()
        and2 = Gate2(LogicGate.AND, x1, gate3_5, gate4)
        gate6 = Wire()
        and3 = Gate2(LogicGate.AND, gate3_5, x3, gate6)
        gate7 = Wire()
        or1 = Gate2(LogicGate.OR, gate2, gate4, gate7)
        gate8 = Wire()
        or2 = Gate2(LogicGate.OR, gate7, gate6, gate8)
        y = gate8
        return [x1, x2, x3], [y]



class Gate2:
    def __init__(self, gateType, inputA=None, inputB=None, output=None):
        self.gateType = gateType
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


class Gate1:
    def __init__(self, gateType, inputA=None, output=None):
        self.gateType = gateType
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