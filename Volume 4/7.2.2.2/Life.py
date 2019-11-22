import pycosat
import math
import numpy as np
import pprint as pp
import sys
import collections
import re
from enum import Enum
from SATUtils import SATUtils
from collections import namedtuple
from GraphColoring import GraphColoring


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
        print(self.game)


class GameInstance:
    def __init__(self,height=0,width=0):
        self.height = height
        self.width = width
        self.tilings = [Tiling(height=height, width=width, time=0)]

    def __getitem__(self, key):
        return self.tilings[key]

    def __str__(self):

        gameStr = '-------------\n'
        for t in range(len(self.tilings)):
            gameStr+= 'Time = ' + str(t) + '\n'
            gameStr+= str(self[t])
            gameStr+= '-------------\n'
        return gameStr


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
                wtfIsThis = self[i][j]
                if self[i][j].state == State.ALIVE:
                    boardStr+= '■'
                elif self[i][j].state == State.DEAD:
                    boardStr+= '□'
                elif self[i][j].state == State.DONTCARE:
                    boardStr+= '▩'
                else:
                    raise Exception('Unknown tile state')

            if i != self.width:
                boardStr+= '\n'
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
                                numAlive+= 1
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
            pass
        elif boundaryCondition == BoundaryCondition.ALL_ALIVE:
            pass
        else:
            raise Exception('Unknown boundary condition')
        return newTiling


class Tile:
    def __init__(self, state=State.DONTCARE, row=-1, col=-1):
        self.state = state
        self.row=row
        self.col=col

    def __str__(self):
        return '[' + str(self.row) + ', ' + str(self.col) + ', ' + self.state.name + ']'

if __name__ == "__main__":
    lifeGame = Life()
    lifeGame.Blinker()
    nextState = lifeGame.game.tilings[0].GetNextState()
    print(lifeGame.game.tilings[0])
    print(nextState)
    test = 0

