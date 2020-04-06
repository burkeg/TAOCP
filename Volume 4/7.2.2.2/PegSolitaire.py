import pycosat
from SATUtils import SATUtils, CNF, Clause, Literal, DSAT, Tseytin, LiteralAllocator
from LogicFormula import *


class PegState(Enum):
    ALIVE = 0
    DEAD = 1
    DONTCARE = 2
    DNE = 3


class PegSolitaire:
    def __init__(self, height=0, width=0):
        self.height = height
        self.width = width
        self.game = None
        self.literalAllocator = LiteralAllocator()
        self.cnf = CNF()

    def Test1D(self):
        self.height = 1
        self.width = 7
        numGen = 3
        self.game = PegGameInstance(height=self.height, width=self.width)
        self.game.boards = [PegBoardState(height=self.height, width=self.width,time=t) for t in range(numGen)]
        self.literalAllocator = LiteralAllocator()
        # Start state
        for i in range(self.width):
            if i != 3:
                self.game[0][0][i].state = PegState.ALIVE
            else:
                self.game[0][0][i].state = PegState.DEAD
        # Intermediate states
        for t in range(1,numGen):
            for i in range(self.width):
                self.game[t][0][i].state = PegState.DONTCARE

    def DefaultGame(self):
        self.height = 7
        self.width = 7
        self.game = PegGameInstance(height=7, width=7)
        self.game.boards = [PegBoardState(height=7, width=7,time=t) for t in range(31)]
        self.literalAllocator = LiteralAllocator()
        # Start state
        for i in range(7):
            for j in range(7):
                if i in range(2,5) or j in range(2,5):
                    if i == j and i == 3:
                        self.game[0][i][j].state = PegState.DEAD
                    else:
                        self.game[0][i][j].state = PegState.ALIVE
        # Intermediate states
        for t in range(1,30):
            for i in range(7):
                for j in range(7):
                    if i in range(2,5) or j in range(2,5):
                        self.game[t][i][j].state = PegState.DONTCARE
        # Final state
        for i in range(7):
            for j in range(7):
                if i in range(2,5) or j in range(2,5):
                    if i == j and i == 3:
                        self.game[30][i][j].state = PegState.ALIVE
                    else:
                        self.game[30][i][j].state = PegState.DEAD

    def BasicTest(self):
        self.height = 5
        self.width = 5
        numGen = 3
        self.game = PegGameInstance(height=self.height, width=self.width)
        self.game.boards = [PegBoardState(height=self.height, width=self.width,time=t) for t in range(numGen)]
        self.literalAllocator = LiteralAllocator()
        # Start state
        for i in range(self.height):
            for j in range(self.width):
                    if i == j and i == 2:
                        self.game[0][i][j].state = PegState.DEAD
                    else:
                        self.game[0][i][j].state = PegState.ALIVE
        # Intermediate states
        for t in range(1,numGen):
            for i in range(self.height):
                for j in range(self.width):
                    self.game[t][i][j].state = PegState.DONTCARE

    def assignLiterals(self):
        for t in range(len(self.game.boards)):
            for i in range(self.height):
                for j in range(self.width):
                    if self.game[t][i][j].state != PegState.DNE:
                        self.game[t][i][j].variable = self.literalAllocator.getLiteral()
        print(self.game)


    def FillInSequence(self):
        sequence = self.game.boards
        if len(sequence) <= 1:
            raise Exception('A sequence needs at least 2 elements!')
        for board in sequence:
            assert isinstance(board, PegBoardState)
            assert board.height == sequence[0].height and board.width == sequence[0].width, \
                'Cannot compare boards with different dimensions.'
        self.assignLiterals()
        height = sequence[0].height
        width = sequence[0].width

        self.assertTransitions()
        self.assertOneMovePerTurn()
        self.assertFixedStates()

        for solution in pycosat.itersolve(self.cnf.rawCNF()):
            updatedSequence = []
            for tiling in sequence:
                newTilingA = PegBoardState(tiling.height, tiling.width, tiling.time)

                for row in range(tiling.height):
                    for col in range(tiling.width):
                        if tiling[row][col].state != PegState.DNE:
                            if tiling[row][col].variable in solution:
                                if tiling[row][col].state == PegState.ALIVE or tiling[row][col].state == PegState.DONTCARE:
                                    # This means that we either forced the cell to be alive or we derived a possible value
                                    newTilingA[row][col].state = PegState.ALIVE
                                else:
                                    # raise Exception("Computed state is incompatible with original state")
                                    pass
                            elif -tiling[row][col].variable in solution:
                                if tiling[row][col].state == PegState.DEAD or tiling[row][col].state == PegState.DONTCARE:
                                    # This means that we either forced the cell to be dead or we derived a possible value
                                    newTilingA[row][col].state = PegState.DEAD
                                    pass
                                else:
                                    # raise Exception("Computed state is incompatible with original state")
                                    pass
                            else:
                                raise Exception("Input wasn't even in the solution! Something is clearly wrong here.")
                updatedSequence.append(newTilingA)
            gameSolution = PegGameInstance()
            gameSolution.SetFrames(updatedSequence)
            print(gameSolution)
            break

    def assertTransitions(self):
        self.assertAllTriplets()


    def assertFixedStates(self):
        fixedVals = []
        for t in range(1): #len(self.game.boards)):
            for row in range(self.height):
                for col in range(self.width):
                    if self.game.boards[t][row][col].state == PegState.ALIVE:
                        fixedVals.append(self.game.boards[t][row][col].variable)
                    if self.game.boards[t][row][col].state == PegState.DEAD:
                        fixedVals.append(-self.game.boards[t][row][col].variable)
        self.cnf.mergeWithRaw([[x] for x in fixedVals])


    def assertTriplet(self, jumper, skipped, endpoint, time):
        a = self.game.boards[time][jumper[0]][jumper[1]].variable
        b = self.game.boards[time][skipped[0]][skipped[1]].variable
        c = self.game.boards[time][endpoint[0]][endpoint[1]].variable
        x = self.game.boards[time + 1][jumper[0]][jumper[1]].variable
        y = self.game.boards[time + 1][skipped[0]][skipped[1]].variable
        z = self.game.boards[time + 1][endpoint[0]][endpoint[1]].variable
        clauses = [
            [-a, -b, c, -x, y],
            [-a, -b, c, -x, -z],
            [-a, -b, c, x, -y],
            [-a, -b, c, -y, -z],
            [-a, -b, c, x, z],
            [-a, -b, c, y, z]
        ]
        self.cnf.mergeWithRaw(clauses)

    def assertAllTriplets(self):
        for t in range(len(self.game.boards) - 1):
            for row in range(self.height):
                for col in range(self.width):
                    for direction in [[-1, 0], [1, 0], [0,-1], [0, 1]]:
                        xDir = direction[0]
                        yDir = direction[1]
                        jumper=[row, col]
                        skipped=[row + xDir, col + yDir]
                        endpoint=[row + 2 * xDir, col + 2 * yDir]
                        if self.isValidTriple(jumper, skipped, endpoint):
                            self.assertTriplet(jumper, skipped, endpoint, t)

    def assertOneMovePerTurn(self):
        initPop = 0
        for row in range(self.height):
            for col in range(self.width):
                if self.game.boards[0][row][col].state == PegState.ALIVE:
                    initPop += 1

        for t in range(len(self.game.boards)):
            boardLiterals = []
            for row in range(self.height):
                for col in range(self.width):
                    if self.game.boards[t][row][col].state != PegState.DNE:
                        boardLiterals.append(self.game.boards[t][row][col].variable)
            # Try swapping for SATUtils.atLeast to check for faster speeds
            newClauses, highestLiteral = SATUtils.exactlyR(boardLiterals, initPop - t, startLiteral=self.literalAllocator.getCurrLiteral())
            if highestLiteral >= self.literalAllocator.getCurrLiteral():
                self.literalAllocator.getLiterals(highestLiteral - self.literalAllocator.getCurrLiteral() + 1)
            self.cnf.mergeWithRaw(newClauses)


    def isValidTriple(self, jumper, skipped, endpoint):
        if endpoint[0] not in range(self.width) or endpoint[1] not in range(self.height):
            return False
        if skipped[0] not in range(self.width) or skipped[1] not in range(self.height):
            return False
        if self.game.boards[0][jumper[0]][jumper[1]].state == PegState.DNE:
            return False
        if self.game.boards[0][skipped[0]][skipped[1]].state == PegState.DNE:
            return False
        if self.game.boards[0][endpoint[0]][endpoint[1]].state == PegState.DNE:
            return False
        return True


class PegGameInstance:
    def __init__(self, height=0, width=0):
        self.height = height
        self.width = width
        self.boards = [PegBoardState(height=height, width=width, time=0)]

    def __getitem__(self, key):
        return self.boards[key]

    def __str__(self):
        gameStr = '-------------\n'
        for t in range(len(self.boards)):
            gameStr += 'Time = ' + str(t) + '\n'
            gameStr += str(self[t])
            gameStr += '-------------\n'
        return gameStr

    def SetFrames(self, frames):
        if len(frames) == 0:
            raise Exception('Why load in 0 frames?')
        for tiling in frames:
            assert isinstance(tiling, PegBoardState), 'Frames must be of type PegBoardState'
            assert tiling.height == frames[0].height and tiling.width == frames[0].width, \
                'Cannot compare PegBoardState with different dimensions.'
        self.boards = frames
        self.width = frames[0].width
        self.height = frames[0].height

class PegBoardState:
    def __init__(self, height=0, width=0, time=0):
        self.height = height
        self.width = width
        self.time = time
        self.board = [[PegBoardTile(row=y, col=x) for x in range(width)] for y in range(height)]

    def __getitem__(self, key):
        return self.board[key]

    def __str__(self):
        boardStr= ''
        for i in range(self.height):
            for j in range(self.width):
                if self[i][j].state == PegState.ALIVE:
                    boardStr += '■'
                elif self[i][j].state == PegState.DEAD:
                    boardStr += '□'
                elif self[i][j].state == PegState.DONTCARE:
                    boardStr += '▩'
                elif self[i][j].state == PegState.DNE:
                    boardStr += '▣'
                else:
                    raise Exception('Unknown tile state')

            if i != self.height:
                boardStr += '\n'
        return boardStr

class PegBoardTile:
    def __init__(self, state=PegState.DNE, row=None, col=None, variable=None, time=None):
        assert issubclass(type(state), Enum)
        self.state = state
        self.row=row
        self.col=col
        self.variable = variable
        self.time = time

    def __str__(self):
        return '[' + str(self.row) + ', ' + str(self.col) + ', ' + self.state.name + ']'

class Testing:
    @staticmethod
    def testTripletClauses():
        ps = PegSolitaire()
        ps.DefaultGame()
        ps.assertTriplet([1, 4], [2, 5], [3, 6])
        print(ps.cnf)
        ps.cnf.mergeWithRaw([[1], [2], [-3]])

        for solution in pycosat.itersolve(ps.cnf.rawCNF()):
            print('----------------------', solution)

if __name__ == '__main__':
    ps = PegSolitaire()
    ps.Test1D()
    ps.FillInSequence()