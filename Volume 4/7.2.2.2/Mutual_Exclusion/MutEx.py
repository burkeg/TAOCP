from abc import ABC, abstractmethod
from SATUtils import SATUtils, Clause, CNF, LiteralAllocator
import pprint as pp
import pycosat

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
                            # Set l <- 1
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

def DoStuff():
    for i in range(10):
        m = Protocol44(i)
        # print(m.cnf)
        # pp.pprint(m.literalMapping)
        m.Solve()


if __name__ == '__main__':
    DoStuff()