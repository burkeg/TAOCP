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
        self.assertedInputWires = self.inputs
        self.detectedInputWires = []
        self.constantWires = []
        if overwriteLiterals:
            LogicFormula.assignVariables(inputs, startLiteral)
        self.usedLiterals = self.getAllUsedVariables(self.inputs)
        if startLiteral is None:
            startLiteral = max(self.usedLiterals) + 1
        self.cnfForm = CNF()
        self.getTseytinCNF()
        self.rawCnf = self.cnfForm.rawCNF()
        self.unusedVars = self.cnfForm.usedVariables().symmetric_difference(set(range(1, max(self.cnfForm.usedVariables()) + 1)))
        assert len(self.unusedVars) == 0, \
            "There shouldn't be unused variables in the Tseytin transform. Something is clearly wrong"


    def getConstantClauses(self, visitedPoints):
        clauses = []
        self.constantWires = []
        for wire in visitedPoints:
            if isinstance(wire, Wire) and wire.constant is not None and wire not in self.constantWires:
                self.constantWires.append(wire)
                if wire.constant:
                    clauses.append([wire.variable])
                else:
                    clauses.append([-wire.variable])
        return clauses

    def getTseytinCNF(self):
        self.cnfForm = CNF()
        if len(self.inputs) == 0:
            return
        visited = []
        componentQueue = deque(self.assertedInputWires)
        # componentQueue = deque(self.inputs)
        visited.append(componentQueue[0])
        visitedGates = set()
        while len(componentQueue) != 0:
            v = componentQueue.popleft()
            if isinstance(v,Wire):
                if v.variable is None:
                    raise Exception('All wire components must have a variable bound.')
                if v not in visited:
                    visited.append(v)
                for gate in v.gatesIn:
                    if gate not in visited:
                        visited.append(gate)
                        componentQueue.append(gate)
                if v.gateOut not in visited and v.gateOut is not None:
                    visited.append(v.gateOut)
                    componentQueue.append(v.gateOut)
            elif issubclass(type(v), Gate):
                if v not in visitedGates:
                    visitedGates.add(v)
                    self.cnfForm.mergeWithRaw(self.getTseytinSingleGate(v))
                if v.output not in visited:
                    visited.append(v.output)
                    componentQueue.append(v.output)
                for inputWire in v.inputs:
                    if inputWire not in visited:
                        visited.append(inputWire)
                        componentQueue.append(inputWire)
            else:
                raise Exception("Logic structure should only contain Wires and Gates")
        print(len(visited))
        self.cnfForm.mergeWithRaw(self.getConstantClauses(visited))

    def getTseytinSingleGate(self, gate):
        if not issubclass(type(gate), Gate):
            raise Exception("Must be of type gate")
        # If you manage to get here with inputs/outputs as None I'm impressed!
        if isinstance(gate, Gate2):
            varA = gate.inputA.variable
            varB = gate.inputB.variable
            varOut = gate.output.variable
            if gate.gateType == LogicStructure.AND:
                # print(str(varA) + ' AND ' + str(varB) + ' = ' + str(varOut))
                newClauses, _= Tseytin.AND(varA, varB, varOut)
                return newClauses
            elif gate.gateType == LogicStructure.NAND:
                newClauses, _= Tseytin.NAND(varA, varB, varOut)
                # print(str(varA) + ' NAND ' + str(varB) + ' = ' + str(varOut))
                return newClauses
            elif gate.gateType == LogicStructure.OR:
                newClauses, _= Tseytin.OR(varA, varB, varOut)
                # print(str(varA) + ' OR ' + str(varB) + ' = ' + str(varOut))
                return newClauses
            elif gate.gateType == LogicStructure.NOR:
                newClauses, _= Tseytin.NOR(varA, varB, varOut)
                # print(str(varA) + ' NOR ' + str(varB) + ' = ' + str(varOut))
                return newClauses
            elif gate.gateType == LogicStructure.XOR:
                newClauses, _= Tseytin.XOR(varA, varB, varOut)
                # print(str(varA) + ' XOR ' + str(varB) + ' = ' + str(varOut))
                return newClauses
            elif gate.gateType == LogicStructure.XNOR:
                newClauses, _= Tseytin.XNOR(varA, varB, varOut)
                # print(str(varA) + ' XNOR ' + str(varB) + ' = ' + str(varOut))
                return newClauses
            elif gate.gateType == LogicStructure.IMPLIES:
                newClauses, _= Tseytin.IMPLIES(varA, varB, varOut)
                # print(str(varA) + ' IMPLIES ' + str(varB) + ' = ' + str(varOut))
                return newClauses
            else:
                raise Exception('Unknown gate')
        elif isinstance(gate, Gate1):
            varA = gate.inputA.variable
            varOut = gate.output.variable
            if gate.gateType == LogicStructure.NOT:
                newClauses, _= Tseytin.NOT(varA, varOut)
                # print('NOT ' + str(varA) + ' = ' + str(varOut))
                return newClauses
            else:
                raise Exception('Unknown gate')
        elif isinstance(gate, GateCustom):
            raise Exception("Custum logic structures aren't always gates")

    def getAllUsedVariables(self, inputs):
        if len(inputs) == 0:
            return []
        self.detectedInputWires = []
        self.freeInputs = []
        visited = []
        componentQueue = deque(inputs)
        usedVariables = []
        visited.append(componentQueue[0])
        while len(componentQueue) != 0:
            v = componentQueue.popleft()
            if isinstance(v,Wire):
                if v.variable is None:
                    raise Exception('All wire components must have a variable bound.')
                elif v.variable not in usedVariables:
                    usedVariables.append(v.variable)
                if v not in visited:
                    visited.append(v)
                if v.gateOut is None:
                    if v not in self.detectedInputWires:
                        self.detectedInputWires.append(v)
                    if v.constant is None and v not in self.freeInputs:
                        self.freeInputs.append(v)
                for gate in v.gatesIn:
                    if gate not in visited:
                        visited.append(gate)
                        componentQueue.append(gate)
                if v.gateOut not in visited and v.gateOut is not None:
                    visited.append(v.gateOut)
                    componentQueue.append(v.gateOut)
            elif issubclass(type(v), Gate):
                if v.output not in visited:
                    visited.append(v.output)
                    componentQueue.append(v.output)
                for inputWire in v.inputs:
                    if inputWire not in visited:
                        visited.append(inputWire)
                        componentQueue.append(inputWire)
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
        visited = []
        componentQueue = deque(inputs)
        visited.append(componentQueue[0])
        while len(componentQueue) != 0:
            v = componentQueue.popleft()
            if isinstance(v,Wire):
                v.variable = literalTracker
                literalTracker += 1
                # if v.name is not None:
                #     print(v.name + ' assigned: ' + str(v.variable))
                if v not in visited:
                    visited.append(v)
                for gate in v.gatesIn:
                    if gate not in visited:
                        # print('Gate added')
                        visited.append(gate)
                        componentQueue.append(gate)
                if v.gateOut not in visited and v.gateOut is not None:
                    visited.append(v.gateOut)
                    componentQueue.append(v.gateOut)
            elif issubclass(type(v), Gate):
                if v.output not in visited:
                    visited.append(v.output)
                    componentQueue.append(v.output)
                    # print('Wire added')
                for inputWire in v.inputs:
                    if inputWire not in visited:
                        visited.append(inputWire)
                        componentQueue.append(inputWire)
                        # print('Wire added')
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
    def __init__(self, gateType, inputs, outputs):
        self.gateType = gateType
        self.inputs = inputs
        self.outputs = outputs
        pass


class GateCustom(Gate):
    def __init__(self):
        super().__init__(LogicStructure.CUSTOM, [], [])

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

    # https://en.wikipedia.org/wiki/Wallace_tree
    # similar approach, but all bits have equal weighting and I don't need to do any preprocessing to find bits
    def SidewaysAdd(self, inputs, outputs=None):
        if len(inputs) == 0:
            raise Exception("Cannot have a 0 bit Comparator")
        if len(inputs) == 1:
            self.inputs = inputs
            self.outputs = [inputs[0]]
            return
        bitBuckets = dict()
        bitBuckets[1] = inputs.copy()
        bitsRemain = True
        while bitsRemain:
            nextBuckets = dict()
            for key, value in bitBuckets.items():
                if len(value) == 1:
                    # Job's done, we've already reduced to 1 bit. Continue onwards
                    nextBuckets.setdefault(key, []).append(value[0])
                    continue
                numHalfAdders = 0
                numFullAdders = 0
                if len(value) % 3 == 0:
                    numHalfAdders = 0
                    numFullAdders = len(value) // 3
                elif len(value) % 3 == 1:
                    numHalfAdders = 2
                    numFullAdders = (len(value)-4) // 3
                else:
                    numHalfAdders = 1
                    numFullAdders = len(value) // 3
                test = 0
                for i in range(numFullAdders):
                    FA_S = Wire()
                    FA_Cout = Wire()
                    FA = GateCustom()
                    FA.FullAdder(
                        A=value[i*3 + 0],
                        B=value[i*3 + 1],
                        Cin=value[i*3 + 2],
                        S=FA_S,
                        Cout=FA_Cout)
                    nextBuckets.setdefault(key, []).append(FA_S)
                    nextBuckets.setdefault(key*2, []).append(FA_Cout)

                for i in range(numHalfAdders):
                    HA_S = Wire()
                    HA_Cout = Wire()
                    HA = GateCustom()
                    HA.HalfAdder(
                        A=value[numFullAdders*3 + i*2 + 0],
                        B=value[numFullAdders*3 + i*2 + 1],
                        S=HA_S,
                        Cout=HA_Cout)
                    nextBuckets.setdefault(key, []).append(HA_S)
                    nextBuckets.setdefault(key*2, []).append(HA_Cout)

            bitBuckets = nextBuckets.copy()
            bitsRemain = sum([1 if len(x) == 1 else 0 for x in bitBuckets.values()]) != len(bitBuckets)

        self.inputs = inputs
        self.outputs = [x[0] for x in bitBuckets.values()]
        if outputs is not None:
            for calculated, passedIn in zip(self.outputs, outputs):
                assert isinstance(passedIn, Wire) and isinstance(calculated, Wire)
                passedIn.mergeIntoThis(calculated)


        # At this point, all lists in bitBuckets should have 1 element

    # Produces a circuit whose output is true when the game of life tiles
    def LIFE_nextState(self, prev9tiles, output):
        prevNeighbors = [
            prev9tiles[0],
            prev9tiles[1],
            prev9tiles[2],
            prev9tiles[3],
            prev9tiles[5],
            prev9tiles[6],
            prev9tiles[7],
            prev9tiles[8],
        ]
        prevCenter = prev9tiles[4]

        two = [Wire(name="Two") for _ in range(4)]
        two[0].constant = False
        two[1].constant = True
        two[2].constant = False
        two[3].constant = False
        three = [Wire(name="Three") for _ in range(4)]
        three[0].constant = True
        three[1].constant = True
        three[2].constant = False
        three[3].constant = False
        sadd = GateCustom()
        liveNeighbors = [Wire() for _ in range(4)]
        sadd.SidewaysAdd(prevNeighbors, liveNeighbors)
        liveNeighbors = sadd.outputs

        # If there's 3 alive then output is True
        aliveFrom3 = Wire()
        eq3 = GateCustom()
        eq3.EqualsExpected(liveNeighbors, three, aliveFrom3)

        # Or there's 2 alive and prevCenter is true!
        aliveFrom2 = Wire()
        twoNeighbors = Wire()
        eq2 = GateCustom()
        eq2.EqualsExpected(liveNeighbors, two, twoNeighbors)
        Gate2(LogicStructure.AND, twoNeighbors, prevCenter, aliveFrom2)

        # If Either of the above conditions are true, then we should output True
        Gate2(LogicStructure.OR, aliveFrom2, aliveFrom3, output)
        self.inputs = prev9tiles
        self.outputs = [output]


    def EqualsExpected(self, inputsActual, inputsExpected, output):
        if len(inputsActual) != len(inputsExpected):
            raise Exception('A and B must have same number of bits!')
        if len(inputsActual) == 0:
            raise Exception("Cannot have a 0 bit Comparator")
        bitsEqual = [Gate2(LogicStructure.XNOR, Ai, Bi).output for Ai, Bi in zip(inputsActual, inputsExpected)]
        eqAND = GateCustom()

        # If all XNORs of inputs are 1, then the two numbers are equal
        eqAND.ANDwide(bitsEqual, output)
        self.inputs = inputsActual + inputsExpected
        self.outputs = [output]


class Gate2(Gate):
    def __init__(self, gateType, inputA=None, inputB=None, output=None):
        super().__init__(gateType, inputs=[], outputs=[])
        if inputA is None:
            self.inputA=Wire(gatesIn=self)
        else:
            self.inputA=inputA
            inputA.gatesIn.append(self)

        if inputB is None:
            self.inputB=Wire(gatesIn=self)
        else:
            self.inputB=inputB
            inputB.gatesIn.append(self)

        if output is None:
            self.output=Wire(gateOut=self)
        else:
            self.output=output
            output.gateOut = self
        self.inputs = [inputA, inputB]
        self.outputs = [output]


class Gate1(Gate):
    def __init__(self, gateType, inputA=None, output=None):
        super().__init__(gateType, inputs=[], outputs=[])
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
        self.inputs = [inputA]
        self.outputs = [output]


class Wire:
    def __init__(self, gateOut=None, gatesIn=None, variable=None, constant=None, name=None):
        self.variable = variable
        if gatesIn is None:
            self.gatesIn = []
        self.gateOut = gateOut
        self.constant = constant
        self.name = name

        if isinstance(gatesIn, list):
            for gate in gatesIn:
                assert issubclass(type(gate), Gate)
            self.gatesIn = gatesIn

        elif issubclass(type(gatesIn), Gate):
            self.gatesIn = [gatesIn]
        elif gatesIn is not None:
            raise Exception("Must pass in a gate or list of gates")

    def mergeIntoThis(self, otherWire):
        assert isinstance(otherWire, Wire)

        if self.constant is None:
            self.constant = otherWire.constant
        elif otherWire.constant is not None and self.constant != otherWire.constant:
            raise Exception('Cannot overwrite original wire constant')

        if self.gateOut is None:
            self.gateOut = otherWire.gateOut
        elif otherWire.gateOut is not None and self.gateOut != otherWire.gateOut:
            raise Exception('Cannot overwrite original wire gateOutput')

        if self.variable is None:
            self.variable = otherWire.variable
        elif otherWire.variable is not None and self.variable != otherWire.variable:
            raise Exception('Cannot overwrite original wire variable')

        if self.gatesIn is None:
            self.gatesIn = otherWire.gatesIn
        elif otherWire.gatesIn is not None:
            self.gatesIn.extend(otherWire.gatesIn)



if __name__ == '__main__':
    theInputs, theOutputs = LogicFormula.WikipediaExample()
    formula = LogicFormula(theInputs, 1, overwriteLiterals=True)
    formula.getTseytinCNF()
    test = 0