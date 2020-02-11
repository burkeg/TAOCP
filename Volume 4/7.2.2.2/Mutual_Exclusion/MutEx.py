from abc import ABC, abstractmethod
from SATUtils import SATUtils, Clause, CNF, LiteralAllocator
import pprint as pp

class Mutex(ABC):
    def __init__(self, r=1):
        self.r = r
        self.la = LiteralAllocator()
        self.clauses = CNF()
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


    def SetStateLiterals(self, stateNums):
        for stateName, stateAmt in stateNums:
            self.stateLiterals[stateName] = self.la.getLiterals(stateAmt)

    def GenClauses(self):
        self.ConfigureStateShape()
        self.ConfigureStateLiterals()
        self.CreateVariables()
        self.GenSTLClauses()
        self.DecorateSTLClauses()
        self.GenStateExclusionClauses()

    def DecorateSTLClauses(self):
        for stateName, timestepClauses in self.stlClauses.items():
            for i, clauses in enumerate(timestepClauses):
                for clause in clauses:
                    newClause = Clause(
                        literals=[self.bumpers[i]*self.bumperMapping[stateName]] + clause,
                        comment='Logic for progressing [' + stateName + '] at time ' + str(i) + '.')
                    self.clauses.addClause(newClause)

    def GenStateExclusionClauses(self):
        for stateName, literalsAtTimet in self.stateLiterals.items():
            for t, literals in enumerate(literalsAtTimet):
                clauses, outLiteral = SATUtils.oneOrLess(inLiterals=literals, startLiteral=self.la.getCurrLiteral())
                self.la.getLiterals(outLiteral - self.la.getCurrLiteral())
                for clause in clauses:
                    self.clauses.addClause(Clause(clause, comment='State [' + stateName + '] binary exclusion clause for time ' + str(t) + '.'))

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


# A0. Maybe go to A1.               B0 Maybe go to B1.
# A1. If l go to A1, else to A2.    B1 If l go to B1 else to B2.
# A2. Set l <- 1 , go to A3.        B2. Set l <- 1, go to B3.
# A3. Critical, go to A4.           B3. Critical, go to B4.
# A4. Set l <- 0, go to A0.         B4. Set l <- 0, go to B0.
class Protocol40(Mutex):
    def __init__(self, r=5):
        super().__init__(r)
        super().GenClauses()

    def CreateVariables(self):
        # only 1 variable, l
        self.variables['l'] = self.la.getLiterals(self.r + 1)

    def GenSTLClauses(self):
        self.stlClauses['A'] = [[] for t in range(self.r)]
        self.stlClauses['B'] = [[] for t in range(self.r)]
        for t in range(self.r):
            # When a thread is bumped it can't remain the same state.
            for stateName, numStates in self.stateShapes:
                for stateNum in range(numStates):
                    self.stlClauses[stateName][t].append(
                        [-self.stateLiterals[stateName][t][stateNum],
                         self.stateLiterals[stateName][t+1][stateNum]])



    def ConfigureStateShape(self):
        self.stateShapes = (('A', 2), ('B', 2))
        self.bumperMapping['A'] = 1
        self.bumperMapping['B'] = -1

if __name__ == '__main__':
    m = Protocol40(5)
    pp.pprint(m.clauses)
