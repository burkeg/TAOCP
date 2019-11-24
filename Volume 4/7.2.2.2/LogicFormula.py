from enum import Enum


class LogicGate(Enum):
    AND = 0
    NAND = 1
    OR = 2
    NOR = 3
    NOT = 4
    XOR = 5


class LogicFormula:
    def __init__(self):
        pass

    # https://en.wikipedia.org/wiki/Tseytin_transformation
    def WikipediaExample(self):
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
    LogicFormula().WikipediaExample()
    test = 0