from abc import ABC, abstractmethod
from SATUtils import SATUtils, Clause, CNF, LiteralAllocator
import pprint as pp
import pycosat
from enum import Enum
import collections

Operation = collections.namedtuple('Operation', 'stateName stateNum optype fields')

class OperationType(Enum):
    MAYBE = 0
    CRITICAL = 1
    SETGO = 2
    IFGOELSE = 3

class Mutex(ABC):
    def __init__(self, r=1):
        self.r = r
        self.la = LiteralAllocator()
        self.cnf = CNF()
        # Dictionary of lists of lists of literals for each state at time t
        # example {A:[[A0_0, A1_0, ...], [A0_1, A1_1, ...]], B:[[B0_0, B1_0, ...], [B0_1, B1_1, ...]]}
        self.stateLiterals = dict()
        # Bumper variables for time t
        self.bumpers = self.la.getLiterals(r)
        # Maps a state name to a bumper truth value
        self.bumperMapping = dict()
        # mapping of variable name to list of literals
        self.variables = dict()
        # mapping of State names to a list of lists of clauses (not including bumper)
        # example {A:[t0_clauses, t1_clauses], B:[t0_clauses, t1_clauses]}
        self.stlClauses = dict()
        self.stateShapes = None
        self.literalMapping = dict()

    def GenClauses(self):
        self.ConfigureStateShape()
        self.ConfigureStateLiterals()
        self.CreateVariables()
        self.GenSTLClauses()
        self.DecorateSTLClauses()
        self.GenStateExclusionClauses()
        self.AssertInitState()
        self.AssertCriticalSectionsOverlap()
        self.RecordLiteralMappings()

    def RecordLiteralMappings(self):
        # traverse state variables
        # example A4_8
        for stateName, literalsAtTimet in self.stateLiterals.items():
            for t, literals in enumerate(literalsAtTimet):
                for i, literal in enumerate(literals):
                    self.literalMapping[abs(literal)] = stateName + str(i) + '_' + str(t)

        # traverse variables
        # example l_4
        for variableName, literalsAtTimet in self.variables.items():
            for t, literal in enumerate(literalsAtTimet):
                self.literalMapping[abs(literal)] = variableName + '_' + str(t)

        # traverse bumpers
        # example l_4
        for t, bumperLiteral in enumerate(self.bumpers):
            self.literalMapping[abs(bumperLiteral)] = '@_' + str(t)

        for clause in self.cnf.clauses:
            for literal in clause.literals:
                literal.shortName = self.literalMapping[abs(literal.value)]

    def Solve(self):
        if pycosat.solve(self.cnf.rawCNF()) != 'UNSAT':
            print('Critical section hit by both threads after ' + str(self.r) + ' or less time steps.')
        else:
            print('Impossible for both threads to enter critical section after ' + str(self.r) + ' time steps.')

    def SetStateLiterals(self, stateNums):
        for stateName, stateAmt in stateNums:
            self.stateLiterals[stateName] = self.la.getLiterals(stateAmt)

    def AssertInitState(self):
        # all variables start at 0
        for variableName, literalsAtTimet in self.variables.items():
            self.cnf.addClause(Clause(
                literals=[-literalsAtTimet[0]],
                comment='Assert variable ' + variableName + ' is initialized to false.'))

        # All states at t=0 are off except for each program's state 0.
        for stateName, literalsAtTimet in self.stateLiterals.items():
            for i, stateLiteral in enumerate(literalsAtTimet[0]):
                if i == 0:
                    self.cnf.addClause(Clause(
                        literals=[stateLiteral],
                        comment='Assert program ' + stateName + ' starts in state 0.'))
                else:
                    self.cnf.addClause(Clause(
                        literals=[-stateLiteral],
                        comment='Assert program ' + stateName + " doesn't start in state " + str(i) + '.'))


    def DecorateSTLClauses(self):
        for stateName, timestepClauses in self.stlClauses.items():
            for i, clauses in enumerate(timestepClauses):
                for clause in clauses:
                    newClause = Clause(
                        literals=[self.bumpers[i]*-self.bumperMapping[stateName]] + clause,
                        comment='Logic for progressing [' + stateName + '] at time ' + str(i) + '.')
                    self.cnf.addClause(newClause)

    def GenStateExclusionClauses(self):
        for stateName, literalsAtTimet in self.stateLiterals.items():
            for t, literals in enumerate(literalsAtTimet):
                if t == 0:
                    continue
                clauses, _ = SATUtils.oneOrLess(inLiterals=literals, startLiteral=self.la.getCurrLiteral(), forceInefficient=True)
                for clause in clauses:
                    self.cnf.addClause(Clause(clause, comment='State [' + stateName + '] binary exclusion clause for time ' + str(t) + '.'))

    def ConfigureStateLiterals(self):
        for stateName, numStates in self.stateShapes:
            self.stateLiterals[stateName] = []
            for t in range(self.r + 1):
                self.stateLiterals[stateName].append(self.la.getLiterals(numStates))

    @abstractmethod
    def CreateVariables(self):
        raise NotImplemented("Implement me please.")

    @abstractmethod
    def GenSTLClauses(self):
        raise NotImplemented("Implement me please.")

    @abstractmethod
    def ConfigureStateShape(self):
        raise NotImplemented("Implement me please.")

    @abstractmethod
    def AssertCriticalSectionsOverlap(self):
        raise NotImplemented("Implement me please.")

class Protocol(Mutex):
    def __init__(self, procedure, r=5):
        assert len(procedure) != 0
        for op in procedure:
            assert isinstance(op, Operation)
        super().__init__(r)
        self.procedure = procedure
        super().GenClauses()

    def CreateVariables(self):
        foundVariables = set()
        for operation in self.procedure:
            if operation.optype == OperationType.IFGOELSE or operation.optype == OperationType.SETGO:
                foundVariables.add(operation.fields[0])

        for variable in foundVariables:
            self.variables[variable] = self.la.getLiterals(self.r + 1)

    def AssertCriticalSectionsOverlap(self):
        for operation in self.procedure:
            if operation.optype == OperationType.CRITICAL:
                stateName = operation.stateName
                stateNum = operation.stateNum
                self.cnf.addClause(Clause(literals=[self.stateLiterals[stateName][self.r][stateNum]]))

    def ConfigureStateShape(self):
        stateCount = dict()
        for op in self.procedure:
            stateCount.setdefault(op.stateName, [0])[0] += 1
        self.stateShapes = []
        for stateName, stateCnts in stateCount.items():
            self.stateShapes.append((stateName, stateCnts[0]))
        self.bumperMapping[self.stateShapes[0][0]] = 1
        self.bumperMapping[self.stateShapes[1][0]] = -1

    def GenSTLClauses(self):
        self.stlClauses[self.stateShapes[0][0]] = [[] for t in range(self.r)]
        self.stlClauses[self.stateShapes[1][0]] = [[] for t in range(self.r)]
        # self.stlClauses['A'] = [[] for t in range(self.r)]
        # self.stlClauses['B'] = [[] for t in range(self.r)]
        for t in range(self.r):
            variableChangingStates = dict()
            for op in self.procedure:
                if op.optype == OperationType.SETGO:
                    variableChangingStates.setdefault((op.fields[0], op.stateName), []).append(op.stateNum)

            for key, stateNums in variableChangingStates.items():
                variable, stateName = key
                clauseTrue = [self.variables[variable][t],
                    -self.variables[variable][t + 1]]
                clauseFalse = [-self.variables[variable][t],
                    self.variables[variable][t + 1]]
                clauseState = []
                for stateNum in stateNums:
                    clauseState.append(self.stateLiterals[stateName][t][stateNum])
                # if variable is true outside of changing states, it better stay true at t+1
                self.stlClauses[stateName][t].append(clauseTrue + clauseState)
                # if variable is false outside of changing states, it better stay true at t+1
                self.stlClauses[stateName][t].append(clauseFalse + clauseState)



            # if variable is true outside of changing states, it better stay true at t+1
            # self.stlClauses['A'][t].append(
            #     [self.variables['l'][t],
            #      self.stateLiterals['A'][t][2],
            #      self.stateLiterals['A'][t][4],
            #      -self.variables['l'][t + 1]])

            for op in self.procedure:
                currState = op.stateName
                otherState = self.stateShapes[0][0] if currState != self.stateShapes[0][0] else self.stateShapes[1][0]
                # When a thread isn't bumped it better be in the same state at t+1
                self.stlClauses[otherState][t].append(
                    [-self.stateLiterals[op.stateName][t][op.stateNum],
                     self.stateLiterals[op.stateName][t + 1][op.stateNum]])

                if op.optype == OperationType.MAYBE:
                    (nextState,) = op.fields
                    nextStateName = nextState[0]
                    nextStateNum = int(nextState[1])
                    # CurrentState. Maybe go to state.
                    self.stlClauses[op.stateName][t].append(
                        [-self.stateLiterals[op.stateName][t][op.stateNum],
                         self.stateLiterals[op.stateName][t + 1][op.stateNum],
                         self.stateLiterals[nextStateName][t + 1][nextStateNum]])
                    # A0. Maybe go to A1.
                    # self.stlClauses[stateName][t].append(
                    #     [-self.stateLiterals['A'][t][0],
                    #      self.stateLiterals['A'][t + 1][0],
                    #      self.stateLiterals['A'][t + 1][1]])
                elif op.optype == OperationType.IFGOELSE:
                    (variable, ifState, elseState) = op.fields
                    ifStateName = ifState[0]
                    ifStateNum = int(ifState[1])
                    elseStateName = elseState[0]
                    elseStateNum = int(elseState[1])
                    # CurrentState. If variable go to state, else to other state.
                    # go to state
                    self.stlClauses[op.stateName][t].append(
                        [-self.stateLiterals[op.stateName][t][op.stateNum],
                         -self.variables[variable][t],
                         self.stateLiterals[ifStateName][t + 1][ifStateNum]])
                    # else go to other state
                    self.stlClauses[op.stateName][t].append(
                        [-self.stateLiterals[op.stateName][t][op.stateNum],
                         self.variables[variable][t],
                         self.stateLiterals[elseStateName][t + 1][elseStateNum]])
                    # # A1. If l go to A1, else to A2.
                    # # go to A1
                    # self.stlClauses[stateName][t].append(
                    #     [-self.stateLiterals['A'][t][1],
                    #      -self.variables['l'][t],
                    #      self.stateLiterals['A'][t + 1][1]])
                    # # else go to A2
                    # self.stlClauses[stateName][t].append(
                    #     [-self.stateLiterals['A'][t][1],
                    #      self.variables['l'][t],
                    #      self.stateLiterals['A'][t + 1][2]])
                elif op.optype == OperationType.SETGO:
                    (variable, truthVal, goState) = op.fields
                    goStateName = goState[0]
                    goStateNum = int(goState[1])
                    # CurrentState. Set variable <- truthVal , go to goState.
                    # go to goState
                    self.stlClauses[op.stateName][t].append(
                        [-self.stateLiterals[op.stateName][t][op.stateNum],
                         self.stateLiterals[goStateName][t + 1][goStateNum]])
                    # Set variable <- truthVal
                    if truthVal:
                        self.stlClauses[stateName][t].append(
                            [-self.stateLiterals[op.stateName][t][op.stateNum],
                             self.variables[variable][t + 1]])
                    else:
                        self.stlClauses[stateName][t].append(
                            [-self.stateLiterals[op.stateName][t][op.stateNum],
                             -self.variables[variable][t + 1]])
                    # # A2. Set l <- 1 , go to A3.
                    # # go to A3
                    # self.stlClauses[stateName][t].append(
                    #     [-self.stateLiterals['A'][t][2],
                    #      self.stateLiterals['A'][t + 1][3]])
                    # # Set l <- 1
                    # self.stlClauses[stateName][t].append(
                    #     [-self.stateLiterals['A'][t][2],
                    #      self.variables['l'][t + 1]])
                elif op.optype == OperationType.CRITICAL:
                    (goState,) = op.fields
                    nextStateName = goState[0]
                    nextStateNum = int(goState[1])
                    # A3. Critical, go to A4.
                    self.stlClauses[op.stateName][t].append(
                        [-self.stateLiterals[op.stateName][t][op.stateNum],
                         self.stateLiterals[nextStateName][t + 1][nextStateNum]])
                    # # A3. Critical, go to A4.
                    # self.stlClauses[stateName][t].append(
                    #     [-self.stateLiterals['A'][t][3],
                    #      self.stateLiterals['A'][t + 1][4]])

class Protocol40_shorter(Protocol):
    def __init__(self, r=5):
        ops = [
            Operation(stateName='A', stateNum=0, optype=OperationType.MAYBE, fields=('A1',)),
            Operation(stateName='A', stateNum=1, optype=OperationType.IFGOELSE, fields=('l', 'A1', 'A2',)),
            Operation(stateName='A', stateNum=2, optype=OperationType.SETGO, fields=('l', True, 'A3',)),
            Operation(stateName='A', stateNum=3, optype=OperationType.CRITICAL, fields=('A4',)),
            Operation(stateName='A', stateNum=4, optype=OperationType.SETGO, fields=('l', False, 'A0',)),
            Operation(stateName='B', stateNum=0, optype=OperationType.MAYBE, fields=('B1',)),
            Operation(stateName='B', stateNum=1, optype=OperationType.IFGOELSE, fields=('l', 'B1', 'B2',)),
            Operation(stateName='B', stateNum=2, optype=OperationType.SETGO, fields=('l', True, 'B3',)),
            Operation(stateName='B', stateNum=3, optype=OperationType.CRITICAL, fields=('B4',)),
            Operation(stateName='B', stateNum=4, optype=OperationType.SETGO, fields=('l', False, 'B0',)),
        ]
        super().__init__(ops, r)

# A0. Maybe go to A1.               B0. Maybe go to B1.
# A1. If l go to A1, else to A2.    B1. If l go to B1 else, to B2.
# A2. Set l <- 1 , go to A3.        B2. Set l <- 1, go to B3.
# A3. Critical, go to A4.           B3. Critical, go to B4.
# A4. Set l <- 0, go to A0.         B4. Set l <- 0, go to B0.
class Protocol40(Mutex):
    def __init__(self, r=5):
        super().__init__(r)
        super().GenClauses()
        self.Check()

    def CreateVariables(self):
        # only 1 variable, l
        self.variables['l'] = self.la.getLiterals(self.r + 1)

    def AssertCriticalSectionsOverlap(self):
        # assert A is in the critical section at the same time as B
        self.cnf.addClause(Clause(literals=[self.stateLiterals['A'][self.r][3]]))
        self.cnf.addClause(Clause(literals=[self.stateLiterals['B'][self.r][3]]))

    def GenSTLClauses(self):
        self.stlClauses['A'] = [[] for t in range(self.r)]
        self.stlClauses['B'] = [[] for t in range(self.r)]
        for t in range(self.r):
            # if l is true outside of A2 or A4, it better stay true at t+1
            self.stlClauses['A'][t].append(
                [self.variables['l'][t],
                 self.stateLiterals['A'][t][2],
                 self.stateLiterals['A'][t][4],
                 -self.variables['l'][t + 1]])
            # if l is false outside of A2 or A4, it better stay false at t+1
            self.stlClauses['A'][t].append(
                [-self.variables['l'][t],
                 self.stateLiterals['A'][t][2],
                 self.stateLiterals['A'][t][4],
                 self.variables['l'][t + 1]])

            # if l is true outside of B2 or B4, it better stay true at t+1
            self.stlClauses['B'][t].append(
                [self.variables['l'][t],
                 self.stateLiterals['B'][t][2],
                 self.stateLiterals['B'][t][4],
                 -self.variables['l'][t + 1]])
            # if l is false outside of B2 or B4, it better stay false at t+1
            self.stlClauses['B'][t].append(
                [-self.variables['l'][t],
                 self.stateLiterals['B'][t][2],
                 self.stateLiterals['B'][t][4],
                 self.variables['l'][t + 1]])

            for stateName, numStates in self.stateShapes:
                for stateNum in range(numStates):
                    # When a thread isn't bumped it better be in the same state at t+1
                    self.stlClauses['B' if stateName == 'A' else 'A'][t].append(
                        [-self.stateLiterals[stateName][t][stateNum],
                         self.stateLiterals[stateName][t + 1][stateNum]])

                    if stateName == 'A':
                        if stateNum == 0:
                            # A0. Maybe go to A1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][0],
                                 self.stateLiterals['A'][t + 1][0],
                                 self.stateLiterals['A'][t + 1][1]])
                        elif stateNum == 1:
                            # A1. If l go to A1, else to A2.
                            # go to A1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 -self.variables['l'][t],
                                 self.stateLiterals['A'][t + 1][1]])
                            # else go to A2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 self.variables['l'][t],
                                 self.stateLiterals['A'][t + 1][2]])
                        elif stateNum == 2:
                            # A2. Set l <- 1 , go to A3.
                            # go to A3
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][2],
                                 self.stateLiterals['A'][t + 1][3]])
                            # Set l <- 1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][2],
                                 self.variables['l'][t + 1]])
                        elif stateNum == 3:
                            # A3. Critical, go to A4.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][3],
                                 self.stateLiterals['A'][t + 1][4]])
                        elif stateNum == 4:
                            # A4. Set l <- 0, go to A0.
                            # go to A0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][4],
                                 self.stateLiterals['A'][t + 1][0]])
                            # Set l <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][4],
                                 -self.variables['l'][t + 1]])
                    elif stateName == 'B':
                        if stateNum == 0:
                            # B0. Maybe go to B1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][0],
                                 self.stateLiterals['B'][t + 1][0],
                                 self.stateLiterals['B'][t + 1][1]])
                        elif stateNum == 1:
                            # B1. If l go to B1, else to B2.

                            # go to B1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 -self.variables['l'][t],
                                 self.stateLiterals['B'][t + 1][1]])
                            # else go to B2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 self.variables['l'][t],
                                 self.stateLiterals['B'][t + 1][2]])
                        elif stateNum == 2:
                            # B2. Set l <- 1, go to B3.
                            # go to B3
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][2],
                                 self.stateLiterals['B'][t + 1][3]])
                            # Set l <- 1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][2],
                                 self.variables['l'][t + 1]])
                        elif stateNum == 3:
                            # B3. Critical, go to B4.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][3],
                                 self.stateLiterals['B'][t + 1][4]])
                        elif stateNum == 4:
                            # B4. Set l <- 0, go to B0.
                            # go to B0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][4],
                                 self.stateLiterals['B'][t + 1][0]])
                            # Set l <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][4],
                                 -self.variables['l'][t + 1]])

    def ConfigureStateShape(self):
        self.stateShapes = (('A', 5), ('B', 5))
        self.bumperMapping['A'] = 1
        self.bumperMapping['B'] = -1

    def Check(self):
        if len(self.cnf.clauses) != 13 + self.r * 50:
            raise Exception('Expected ' + str(13 + self.r * 50) + ' clauses, generated ' + str(len(self.cnf.clauses)))
        if self.la.getCurrLiteral() != 11 + self.r * 12 + 1:
            raise Exception(
                'Expected ' + str(11 + self.r * 12 + 1) + ' literals, generated ' + str(self.la.getCurrLiteral()))


# A0. Maybe go to A1.               B0. Maybe go to B1.
# A1. If l go to A2, else to A1.    B1. If l go to B1 else, to B2.
# A2. Critical, go to A3.           B2. Critical, go to B3.
# A3. Set l <- 0, go to A0.         B3. Set l <- 1, go to B0.
class Protocol43(Mutex):
    def __init__(self, r=5):
        super().__init__(r)
        super().GenClauses()
        # self.Check()

    def CreateVariables(self):
        # only 1 variable, l
        self.variables['l'] = self.la.getLiterals(self.r + 1)

    def AssertCriticalSectionsOverlap(self):
        # assert A is in the critical section at the same time as B
        self.cnf.addClause(Clause(literals=[self.stateLiterals['A'][self.r][2]]))
        self.cnf.addClause(Clause(literals=[self.stateLiterals['B'][self.r][2]]))

    def GenSTLClauses(self):
        self.stlClauses['A'] = [[] for t in range(self.r)]
        self.stlClauses['B'] = [[] for t in range(self.r)]
        for t in range(self.r):
            # if l is true outside of A3, it better stay true at t+1
            self.stlClauses['A'][t].append(
                [self.variables['l'][t],
                 self.stateLiterals['A'][t][3],
                 -self.variables['l'][t + 1]])
            # if l is false outside of A3, it better stay false at t+1
            self.stlClauses['A'][t].append(
                [-self.variables['l'][t],
                 self.stateLiterals['A'][t][3],
                 self.variables['l'][t + 1]])

            # if l is true outside of B3, it better stay true at t+1
            self.stlClauses['B'][t].append(
                [self.variables['l'][t],
                 self.stateLiterals['B'][t][3],
                 -self.variables['l'][t + 1]])
            # if l is false outside of B3, it better stay false at t+1
            self.stlClauses['B'][t].append(
                [-self.variables['l'][t],
                 self.stateLiterals['B'][t][3],
                 self.variables['l'][t + 1]])

            for stateName, numStates in self.stateShapes:
                for stateNum in range(numStates):
                    # When a thread isn't bumped it better be in the same state at t+1
                    self.stlClauses['B' if stateName == 'A' else 'A'][t].append(
                        [-self.stateLiterals[stateName][t][stateNum],
                         self.stateLiterals[stateName][t + 1][stateNum]])

                    if stateName == 'A':
                        if stateNum == 0:
                            # A0. Maybe go to A1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][0],
                                 self.stateLiterals['A'][t + 1][0],
                                 self.stateLiterals['A'][t + 1][1]])
                        elif stateNum == 1:
                            # A1. If l go to A2, else to A1.
                            # go to A2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 -self.variables['l'][t],
                                 self.stateLiterals['A'][t + 1][2]])
                            # else go to A1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 self.variables['l'][t],
                                 self.stateLiterals['A'][t + 1][1]])
                        elif stateNum == 2:
                            # A2. Critical, go to A3.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][2],
                                 self.stateLiterals['A'][t + 1][3]])
                        elif stateNum == 3:
                            # A3. Set l <- 0, go to A0.
                            # go to A0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][3],
                                 self.stateLiterals['A'][t + 1][0]])
                            # Set l <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][3],
                                 -self.variables['l'][t + 1]])
                    elif stateName == 'B':
                        if stateNum == 0:
                            # B0. Maybe go to B1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][0],
                                 self.stateLiterals['B'][t + 1][0],
                                 self.stateLiterals['B'][t + 1][1]])
                        elif stateNum == 1:
                            # B1. If l go to B1, else to B2.

                            # go to B1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 -self.variables['l'][t],
                                 self.stateLiterals['B'][t + 1][1]])
                            # else go to B2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 self.variables['l'][t],
                                 self.stateLiterals['B'][t + 1][2]])
                        elif stateNum == 2:
                            # B2. Critical, go to B3.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][2],
                                 self.stateLiterals['B'][t + 1][3]])
                        elif stateNum == 3:
                            # B3. Set l <- 1, go to B0.
                            # go to B0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][3],
                                 self.stateLiterals['B'][t + 1][0]])
                            # Set l <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][3],
                                 self.variables['l'][t + 1]])

    def ConfigureStateShape(self):
        self.stateShapes = (('A', 4), ('B', 4))
        self.bumperMapping['A'] = 1
        self.bumperMapping['B'] = -1

# A0. Maybe go to A1.               B0. Maybe go to B1.
# A1. If b go to A1, else to A2.    B1. If a go to B1, else to B2.
# A2. Set a <- 1 , go to A3.        B2. Set b <- 1, go to B3.
# A3. Critical, go to A4.           B3. Critical, go to B4.
# A4. Set a <- 0, go to A0.         B4. Set b <- 0, go to B0.
class Protocol44(Mutex):
    def __init__(self, r=5):
        super().__init__(r)
        super().GenClauses()

    def CreateVariables(self):
        # 2 variables, a and b
        self.variables['a'] = self.la.getLiterals(self.r + 1)
        self.variables['b'] = self.la.getLiterals(self.r + 1)

    def AssertCriticalSectionsOverlap(self):
        # assert A is in the critical section at the same time as B
        self.cnf.addClause(Clause(literals=[self.stateLiterals['A'][self.r][3]]))
        self.cnf.addClause(Clause(literals=[self.stateLiterals['B'][self.r][3]]))

    def GenSTLClauses(self):
        self.stlClauses['A'] = [[] for t in range(self.r)]
        self.stlClauses['B'] = [[] for t in range(self.r)]
        for t in range(self.r):
            # if a is true outside of A2 or A4, it better stay true at t+1
            self.stlClauses['A'][t].append(
                [self.variables['a'][t],
                 self.stateLiterals['A'][t][2],
                 self.stateLiterals['A'][t][4],
                 -self.variables['a'][t + 1]])
            # if a is false outside of A2 or A4, it better stay false at t+1
            self.stlClauses['A'][t].append(
                [-self.variables['a'][t],
                 self.stateLiterals['A'][t][2],
                 self.stateLiterals['A'][t][4],
                 self.variables['a'][t + 1]])

            # if a is true outside of B2 or B4, it better stay true at t+1
            self.stlClauses['B'][t].append(
                [self.variables['a'][t],
                 self.stateLiterals['B'][t][2],
                 self.stateLiterals['B'][t][4],
                 -self.variables['a'][t + 1]])
            # if a is false outside of B2 or B4, it better stay false at t+1
            self.stlClauses['B'][t].append(
                [-self.variables['a'][t],
                 self.stateLiterals['B'][t][2],
                 self.stateLiterals['B'][t][4],
                 self.variables['a'][t + 1]])

            # if b is true outside of A2 or A4, it better stay true at t+1
            self.stlClauses['A'][t].append(
                [self.variables['b'][t],
                 self.stateLiterals['A'][t][2],
                 self.stateLiterals['A'][t][4],
                 -self.variables['b'][t + 1]])
            # if b is false outside of A2 or A4, it better stay false at t+1
            self.stlClauses['A'][t].append(
                [-self.variables['b'][t],
                 self.stateLiterals['A'][t][2],
                 self.stateLiterals['A'][t][4],
                 self.variables['b'][t + 1]])

            # if b is true outside of B2 or B4, it better stay true at t+1
            self.stlClauses['B'][t].append(
                [self.variables['b'][t],
                 self.stateLiterals['B'][t][2],
                 self.stateLiterals['B'][t][4],
                 -self.variables['b'][t + 1]])
            # if b is false outside of B2 or B4, it better stay false at t+1
            self.stlClauses['B'][t].append(
                [-self.variables['b'][t],
                 self.stateLiterals['B'][t][2],
                 self.stateLiterals['B'][t][4],
                 self.variables['b'][t + 1]])

            for stateName, numStates in self.stateShapes:
                for stateNum in range(numStates):
                    # When a thread isn't bumped it better be in the same state at t+1
                    self.stlClauses['B' if stateName == 'A' else 'A'][t].append(
                        [-self.stateLiterals[stateName][t][stateNum],
                         self.stateLiterals[stateName][t + 1][stateNum]])

                    if stateName == 'A':
                        if stateNum == 0:
                            # A0. Maybe go to A1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][0],
                                 self.stateLiterals['A'][t + 1][0],
                                 self.stateLiterals['A'][t + 1][1]])
                        elif stateNum == 1:
                            # A1. If b go to A1, else to A2.
                            # go to A1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 -self.variables['b'][t],
                                 self.stateLiterals['A'][t + 1][1]])
                            # else go to A2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 self.variables['b'][t],
                                 self.stateLiterals['A'][t + 1][2]])
                        elif stateNum == 2:
                            # A2. Set a <- 1 , go to A3.
                            # go to A3
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][2],
                                 self.stateLiterals['A'][t + 1][3]])
                            # Set a <- 1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][2],
                                 self.variables['a'][t + 1]])
                        elif stateNum == 3:
                            # A3. Critical, go to A4.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][3],
                                 self.stateLiterals['A'][t + 1][4]])
                        elif stateNum == 4:
                            # A4. Set a <- 0, go to A0.
                            # go to A0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][4],
                                 self.stateLiterals['A'][t + 1][0]])
                            # Set a <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][4],
                                 -self.variables['a'][t + 1]])
                    elif stateName == 'B':
                    # A0. Maybe go to A1.               B0. Maybe go to B1.
                    # A1. If b go to A1, else to A2.    B1. If a go to B1, else to B2.
                    # A2. Set a <- 1 , go to A3.        B2. Set b <- 1, go to B3.
                    # A3. Critical, go to A4.           B3. Critical, go to B4.
                    # A4. Set a <- 0, go to A0.         B4. Set b <- 0, go to B0.
                        if stateNum == 0:
                            # B0. Maybe go to B1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][0],
                                 self.stateLiterals['B'][t + 1][0],
                                 self.stateLiterals['B'][t + 1][1]])
                        elif stateNum == 1:
                            # B1. If a go to B1, else to B2.

                            # go to B1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 -self.variables['a'][t],
                                 self.stateLiterals['B'][t + 1][1]])
                            # else go to B2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 self.variables['a'][t],
                                 self.stateLiterals['B'][t + 1][2]])
                        elif stateNum == 2:
                            # B2. Set b <- 1, go to B3.
                            # go to B3
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][2],
                                 self.stateLiterals['B'][t + 1][3]])
                            # Set b <- 1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][2],
                                 self.variables['b'][t + 1]])
                        elif stateNum == 3:
                            # B3. Critical, go to B4.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][3],
                                 self.stateLiterals['B'][t + 1][4]])
                        elif stateNum == 4:
                            # B4. Set b <- 0, go to B0.
                            # go to B0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][4],
                                 self.stateLiterals['B'][t + 1][0]])
                            # Set l <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][4],
                                 -self.variables['b'][t + 1]])

    def ConfigureStateShape(self):
        self.stateShapes = (('A', 5), ('B', 5))
        self.bumperMapping['A'] = 1
        self.bumperMapping['B'] = -1

# A0. Maybe go to A1.               B0. Maybe go to B1.
# A1. Set a <- 1 , go to A2.        B1. Set b <- 1, go to B2.
# A2. If b go to A2, else to A3.    B2. If a go to B2, else to B3.
# A3. Critical, go to A4.           B3. Critical, go to B4.
# A4. Set a <- 0, go to A0.         B4. Set b <- 0, go to B0.
class Protocol45(Mutex):
    def __init__(self, r=5):
        super().__init__(r)
        super().GenClauses()

    def CreateVariables(self):
        # 2 variables, a and b
        self.variables['a'] = self.la.getLiterals(self.r + 1)
        self.variables['b'] = self.la.getLiterals(self.r + 1)

    def AssertCriticalSectionsOverlap(self):
        # assert A is in the critical section at the same time as B
        self.cnf.addClause(Clause(literals=[self.stateLiterals['A'][self.r][3]]))
        self.cnf.addClause(Clause(literals=[self.stateLiterals['B'][self.r][3]]))

    def GenSTLClauses(self):
        self.stlClauses['A'] = [[] for t in range(self.r)]
        self.stlClauses['B'] = [[] for t in range(self.r)]
        for t in range(self.r):
            # if a is true outside of A1 or A4, it better stay true at t+1
            self.stlClauses['A'][t].append(
                [self.variables['a'][t],
                 self.stateLiterals['A'][t][1],
                 self.stateLiterals['A'][t][4],
                 -self.variables['a'][t + 1]])
            # if a is false outside of A1 or A4, it better stay false at t+1
            self.stlClauses['A'][t].append(
                [-self.variables['a'][t],
                 self.stateLiterals['A'][t][1],
                 self.stateLiterals['A'][t][4],
                 self.variables['a'][t + 1]])

            # if a is true outside of B1 or B4, it better stay true at t+1
            self.stlClauses['B'][t].append(
                [self.variables['a'][t],
                 self.stateLiterals['B'][t][1],
                 self.stateLiterals['B'][t][4],
                 -self.variables['a'][t + 1]])
            # if a is false outside of B1 or B4, it better stay false at t+1
            self.stlClauses['B'][t].append(
                [-self.variables['a'][t],
                 self.stateLiterals['B'][t][1],
                 self.stateLiterals['B'][t][4],
                 self.variables['a'][t + 1]])

            # if b is true outside of A1 or A4, it better stay true at t+1
            self.stlClauses['A'][t].append(
                [self.variables['b'][t],
                 self.stateLiterals['A'][t][1],
                 self.stateLiterals['A'][t][4],
                 -self.variables['b'][t + 1]])
            # if b is false outside of A1 or A4, it better stay false at t+1
            self.stlClauses['A'][t].append(
                [-self.variables['b'][t],
                 self.stateLiterals['A'][t][1],
                 self.stateLiterals['A'][t][4],
                 self.variables['b'][t + 1]])

            # if b is true outside of B1 or B4, it better stay true at t+1
            self.stlClauses['B'][t].append(
                [self.variables['b'][t],
                 self.stateLiterals['B'][t][1],
                 self.stateLiterals['B'][t][4],
                 -self.variables['b'][t + 1]])
            # if b is false outside of B1 or B4, it better stay false at t+1
            self.stlClauses['B'][t].append(
                [-self.variables['b'][t],
                 self.stateLiterals['B'][t][1],
                 self.stateLiterals['B'][t][4],
                 self.variables['b'][t + 1]])

            for stateName, numStates in self.stateShapes:
                for stateNum in range(numStates):
                    # When a thread isn't bumped it better be in the same state at t+1
                    self.stlClauses['B' if stateName == 'A' else 'A'][t].append(
                        [-self.stateLiterals[stateName][t][stateNum],
                         self.stateLiterals[stateName][t + 1][stateNum]])

                    if stateName == 'A':
                        if stateNum == 0:
                            # A0. Maybe go to A1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][0],
                                 self.stateLiterals['A'][t + 1][0],
                                 self.stateLiterals['A'][t + 1][1]])
                        elif stateNum == 1:
                            # A1. Set a <- 1 , go to A2.
                            # go to A2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 self.stateLiterals['A'][t + 1][2]])
                            # Set a <- 1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][1],
                                 self.variables['a'][t + 1]])
                        elif stateNum == 2:
                            # A2. If b go to A2, else to A3.
                            # IF b go to A2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][2],
                                 -self.variables['b'][t],
                                 self.stateLiterals['A'][t + 1][2]])
                            # else go to A3
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][2],
                                 self.variables['b'][t],
                                 self.stateLiterals['A'][t + 1][3]])
                        elif stateNum == 3:
                            # A3. Critical, go to A4.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][3],
                                 self.stateLiterals['A'][t + 1][4]])
                        elif stateNum == 4:
                            # A4. Set a <- 0, go to A0.
                            # go to A0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][4],
                                 self.stateLiterals['A'][t + 1][0]])
                            # Set a <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['A'][t][4],
                                 -self.variables['a'][t + 1]])
                    elif stateName == 'B':
                    # A0. Maybe go to A1.               B0. Maybe go to B1.
                    # A1. Set a <- 1 , go to A2.        B1. Set b <- 1, go to B2.
                    # A2. If b go to A2, else to A3.    B2. If a go to B2, else to B3.
                    # A3. Critical, go to A4.           B3. Critical, go to B4.
                    # A4. Set a <- 0, go to A0.         B4. Set b <- 0, go to B0.
                        if stateNum == 0:
                            # B0. Maybe go to B1.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][0],
                                 self.stateLiterals['B'][t + 1][0],
                                 self.stateLiterals['B'][t + 1][1]])
                        elif stateNum == 1:
                            # B1. Set b <- 1, go to B2.
                            # go to B2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 self.stateLiterals['B'][t + 1][2]])
                            # Set b <- 1
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][1],
                                 self.variables['b'][t + 1]])
                        elif stateNum == 2:
                            # B2. If a go to B2, else to B3.

                            # If a go to B2
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][2],
                                 -self.variables['a'][t],
                                 self.stateLiterals['B'][t + 1][2]])
                            # else go to B3
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][2],
                                 self.variables['a'][t],
                                 self.stateLiterals['B'][t + 1][3]])
                        elif stateNum == 3:
                            # B3. Critical, go to B4.
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][3],
                                 self.stateLiterals['B'][t + 1][4]])
                        elif stateNum == 4:
                            # B4. Set b <- 0, go to B0.
                            # go to B0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][4],
                                 self.stateLiterals['B'][t + 1][0]])
                            # Set l <- 0
                            self.stlClauses[stateName][t].append(
                                [-self.stateLiterals['B'][t][4],
                                 -self.variables['b'][t + 1]])

    def ConfigureStateShape(self):
        self.stateShapes = (('A', 5), ('B', 5))
        self.bumperMapping['A'] = 1
        self.bumperMapping['B'] = -1

def DoStuff():
    m = Protocol40_shorter(5)
    m.Solve()
    m = Protocol40_shorter(6)
    m.Solve()
    # for i in range(10):
    #     m = Protocol45(i)
    #     # print(m.cnf)
    #     # pp.pprint(m.literalMapping)
    #     m.Solve()


if __name__ == '__main__':
    DoStuff()