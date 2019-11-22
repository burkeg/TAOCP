# import pycosat
# import math
# import numpy as np
# import pprint as pp
# import sys
# import collections
# import re
from enum import Enum
from SATUtils import SATUtils, CNF, Clause, Literal, DSAT
# from collections import namedtuple
# from GraphColoring import GraphColoring


class State(Enum):
    ALIVE = 0
    DEAD = 1
    DONTCARE = 2


class BoundaryCondition(Enum):
    TOROIDAL = 0
    ALL_DEAD = 1
    ALL_ALIVE = 2


class Life:
    def __init__(self,height=0,width=0):
        self.height = height
        self.width = width
        self.game = GameInstance(self.height, self.width)
        # for t in range(1):
        #     for row in range(self.height):
        #         for col in range(self.width):
        #             print(self.game[t][row][col])
        # for t in range(1):
        #     print(self.game[t])
        # print(self.game)

    def Blinker(self):
        self.width = 5
        self.height = 5
        self.game = GameInstance(self.height, self.width)
        for i in range(5):
            for j in range(5):
                self.game[0][i][j].state = State.DEAD
        self.game[0][2][1].state = State.ALIVE
        self.game[0][2][2].state = State.ALIVE
        self.game[0][2][3].state = State.ALIVE

    def Glider(self):
        self.width = 5
        self.height = 5
        self.game = GameInstance(self.height, self.width)
        for i in range(5):
            for j in range(5):
                self.game[0][i][j].state = State.DEAD
        self.game[0][1][2].state = State.ALIVE
        self.game[0][2][1].state = State.ALIVE
        self.game[0][3][1].state = State.ALIVE
        self.game[0][3][2].state = State.ALIVE
        self.game[0][3][3].state = State.ALIVE

    def Gabe(self):
        self.height = 8
        self.width = 21
        self.game = GameInstance(self.height, self.width)
        for row in range(self.height):
            for col in range(self.width):
                self.game[0][row][col].state = State.DEAD
        self.game[0][1][2].state = State.ALIVE
        self.game[0][1][3].state = State.ALIVE
        self.game[0][1][4].state = State.ALIVE
        self.game[0][1][6].state = State.ALIVE
        self.game[0][1][7].state = State.ALIVE
        self.game[0][1][8].state = State.ALIVE
        self.game[0][1][11].state = State.ALIVE
        self.game[0][1][12].state = State.ALIVE
        self.game[0][1][13].state = State.ALIVE
        self.game[0][1][16].state = State.ALIVE
        self.game[0][1][17].state = State.ALIVE
        self.game[0][1][18].state = State.ALIVE
        self.game[0][1][19].state = State.ALIVE


        self.game[0][2][1].state = State.ALIVE

        self.game[0][2][6].state = State.ALIVE
        self.game[0][2][9].state = State.ALIVE

        self.game[0][2][11].state = State.ALIVE
        self.game[0][2][14].state = State.ALIVE

        self.game[0][2][16].state = State.ALIVE


        self.game[0][3][1].state = State.ALIVE
        self.game[0][3][3].state = State.ALIVE
        self.game[0][3][4].state = State.ALIVE

        self.game[0][3][6].state = State.ALIVE
        self.game[0][3][7].state = State.ALIVE
        self.game[0][3][8].state = State.ALIVE
        self.game[0][3][9].state = State.ALIVE

        self.game[0][3][11].state = State.ALIVE
        self.game[0][3][12].state = State.ALIVE
        self.game[0][3][13].state = State.ALIVE

        self.game[0][3][16].state = State.ALIVE
        self.game[0][3][17].state = State.ALIVE
        self.game[0][3][18].state = State.ALIVE

        self.game[0][4][1].state = State.ALIVE
        self.game[0][4][4].state = State.ALIVE

        self.game[0][4][6].state = State.ALIVE
        self.game[0][4][9].state = State.ALIVE

        self.game[0][4][11].state = State.ALIVE
        self.game[0][4][14].state = State.ALIVE

        self.game[0][4][16].state = State.ALIVE


        self.game[0][5][1].state = State.ALIVE
        self.game[0][5][4].state = State.ALIVE

        self.game[0][5][6].state = State.ALIVE
        self.game[0][5][9].state = State.ALIVE

        self.game[0][5][11].state = State.ALIVE
        self.game[0][5][14].state = State.ALIVE

        self.game[0][5][16].state = State.ALIVE


        self.game[0][6][2].state = State.ALIVE
        self.game[0][6][3].state = State.ALIVE
        self.game[0][6][4].state = State.ALIVE

        self.game[0][6][6].state = State.ALIVE
        self.game[0][6][9].state = State.ALIVE

        self.game[0][6][11].state = State.ALIVE
        self.game[0][6][12].state = State.ALIVE
        self.game[0][6][13].state = State.ALIVE

        self.game[0][6][16].state = State.ALIVE
        self.game[0][6][17].state = State.ALIVE
        self.game[0][6][18].state = State.ALIVE
        self.game[0][6][19].state = State.ALIVE

    def Assert_A_Precedes_B(self, A, B, boundaryCondition=BoundaryCondition.ALL_DEAD):
        if A.height != B.height or A.width != B.width:
            raise Exception('Cannot compare tilings with different dimensions.')
        for row in range(A.height):
            for col in range(A.width):
                if A[row][col].variable == None or B[row][col].variable == None:
                    raise Exception('All tiles must have a variable tied to them.')

        #   TODO
        #   adj = [
        #       A[i-1][j-1],
        #       A[i-1][j],
        #       A[i-1][j+1],
        #       A[i][j-1],
        #       A[i][j+1],
        #       A[i+1][j-1],
        #       A[i+1][j],
        #       A[i+1][j+1],
        #   ]
        #   POPCNT() counts the number of true variables in the list
        #   (POPCNT(adj) == 3 or (POPCNT(adj) == 2 and A[i][j])) implies B[i][j]

        if boundaryCondition == BoundaryCondition.ALL_DEAD:
            clauses=CNF()
        else:
            raise NotImplementedError()

class GameInstance:
    def __init__(self, height=0, width=0, boundaryCondition=BoundaryCondition.TOROIDAL):
        self.height = height
        self.width = width
        self.boundaryCondition = boundaryCondition
        self.tilings = [Tiling(height=height, width=width, time=0)]

    def __getitem__(self, key):
        return self.tilings[key]

    def __str__(self):

        gameStr = '-------------\n'
        for t in range(len(self.tilings)):
            gameStr += 'Time = ' + str(t) + '\n'
            gameStr += str(self[t])
            gameStr += '-------------\n'
        return gameStr

    def AddFrames(self, n):
        if len(self.tilings) == 0:
            return
        for i in range(n):
            self.tilings.append(self.tilings[-1].GetNextState(boundaryCondition=self.boundaryCondition))


class Tiling:
    def __init__(self,height=0,width=0,time=-1):
        self.height = height
        self.width = width
        self.time = time
        self.board = [[Tile(row=y, col=x) for x in range(width)] for y in range(height)]

    def __getitem__(self, key):
        return self.board[key]

    def __str__(self):
        boardStr= ''
        for i in range(self.height):
            for j in range(self.width):
                if self[i][j].state == State.ALIVE:
                    boardStr += '■'
                elif self[i][j].state == State.DEAD:
                    boardStr += '□'
                elif self[i][j].state == State.DONTCARE:
                    boardStr += '▩'
                else:
                    raise Exception('Unknown tile state')

            if i != self.width:
                boardStr += '\n'
        return boardStr

    def GetNextState(self, boundaryCondition=BoundaryCondition.TOROIDAL):
        newTiling = Tiling(height=self.height, width=self.width, time=self.time + 1)
        offsets = [-1, 0, 1]
        if boundaryCondition == BoundaryCondition.TOROIDAL:
            for row in range(self.height):
                for col in range(self.width):
                    numAlive = 0
                    for i in offsets:
                        for j in offsets:
                            adjustedRow = (row + i) % self.height
                            adjustedCol = (col + j) % self.width
                            if self[adjustedRow][adjustedCol].state == State.ALIVE and not(i == 0 and j == 0):
                                numAlive += 1
                    # Live cells stay alive when they have 2 or 3 neighbors
                    if self[row][col].state == State.ALIVE and (numAlive == 2 or numAlive == 3):
                        newTiling[row][col].state = State.ALIVE
                        # Dead cells come alive when they have exactly 3 neighbors
                    elif self[row][col].state == State.DEAD and numAlive == 3:
                        newTiling[row][col].state = State.ALIVE
                        # All other remaining cells become dead
                    else:
                        newTiling[row][col].state = State.DEAD

        elif boundaryCondition == BoundaryCondition.ALL_DEAD:
            for row in range(self.height):
                for col in range(self.width):
                    numAlive = 0
                    for i in offsets:
                        for j in offsets:
                            adjustedRow = row + i
                            adjustedCol = col + j
                            # Out of bounds cells count as dead
                            if adjustedRow not in range(self.height) or adjustedCol not in range(self.width):
                                numAlive += 0
                            elif self[adjustedRow][adjustedCol].state == State.ALIVE and not(i == 0 and j == 0):
                                numAlive += 1
                    # Live cells stay alive when they have 2 or 3 neighbors
                    if self[row][col].state == State.ALIVE and (numAlive == 2 or numAlive == 3):
                        newTiling[row][col].state = State.ALIVE
                        # Dead cells come alive when they have exactly 3 neighbors
                    elif self[row][col].state == State.DEAD and numAlive == 3:
                        newTiling[row][col].state = State.ALIVE
                        # All other remaining cells become dead
                    else:
                        newTiling[row][col].state = State.DEAD

        elif boundaryCondition == BoundaryCondition.ALL_ALIVE:
            for row in range(self.height):
                for col in range(self.width):
                    numAlive = 0
                    for i in offsets:
                        for j in offsets:
                            adjustedRow = row + i
                            adjustedCol = col + j
                            # Out of bounds cells count as alive
                            if adjustedRow not in range(self.height) or adjustedCol not in range(self.width):
                                numAlive += 1
                            elif self[adjustedRow][adjustedCol].state == State.ALIVE and not(i == 0 and j == 0):
                                numAlive += 1
                    # Live cells stay alive when they have 2 or 3 neighbors
                    if self[row][col].state == State.ALIVE and (numAlive == 2 or numAlive == 3):
                        newTiling[row][col].state = State.ALIVE
                        # Dead cells come alive when they have exactly 3 neighbors
                    elif self[row][col].state == State.DEAD and numAlive == 3:
                        newTiling[row][col].state = State.ALIVE
                        # All other remaining cells become dead
                    else:
                        newTiling[row][col].state = State.DEAD
        else:
            raise Exception('Unknown boundary condition')
        return newTiling


class Tile:
    def __init__(self, state=State.DONTCARE, row=-1, col=-1, variable=None):
        self.state = state
        self.row=row
        self.col=col
        self.variable = variable

    def __str__(self):
        return '[' + str(self.row) + ', ' + str(self.col) + ', ' + self.state.name + ']'

if __name__ == "__main__":
    lifeGame = Life(5, 5)
    tilingA = Tiling(5,5)
    tilingB = Tiling(5,5)
    variableCount = 1
    for i in range(5):
        for j in range(5):
            tilingA[i][j].variable = variableCount
            variableCount += 1
    for i in range(5):
        for j in range(5):
            tilingB[i][j].variable = variableCount
            variableCount += 1
    lifeGame.Assert_A_Precedes_B(tilingA, tilingB)
    test = 0

