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

class Life:
    def  __init__(self,height=0,width=0):
        self.height = height
        self.width = width
        self.game = GameInstance(self.height, self.width)
        for t in range(1):
            for x in range(self.height):
                for y in range(self.width):
                    print(self.game[t][x][y])
        for t in range(1):
            print(self.game[t])
        print(self.game)
        pass

class GameInstance:
    def  __init__(self,height=0,width=0):
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
    def  __init__(self,height=0,width=0,time=-1):
        self.height = height
        self.width = width
        self.time = time
        self.board = [[Tile(x=x,y=y) for x in range(width)] for y in range(height)]

    def __getitem__(self, key):
        return self.board[key]

    def __str__(self):
        boardStr= ''
        for i in range(self.height):
            for j in range(self.width):
                if self[i][j] == State.ALIVE:
                    boardStr+= '■'
                elif self[i][j] == State.DEAD:
                    boardStr+= '□'
                else:
                    boardStr+= '▩'
            if i != self.width:
                boardStr+= '\n'
        return boardStr

class Tile:
    def __init__(self, state=State.DONTCARE, x=-1, y=-1):
        self.state = state
        self.x=x
        self.y=y

    def __str__(self):
        return '[' + str(self.x) + ', ' + str(self.y) + ', ' + self.state.name + ']'

if __name__ == "__main__":
    Life(3,7)
