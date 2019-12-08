import pycosat
# import math
# import numpy as np
# import pprint as pp
# import sys
# import collections
# import re
import time
import os
from enum import Enum
from SATUtils import SATUtils, CNF, Clause, Literal, DSAT, Tseytin
from LogicFormula import *
from Life import *
# from collections import namedtuple
# from GraphColoring import GraphColoring

class MSState(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 6
    SIX = 5
    SEVEN = 7
    EIGHT = 8
    UNKNOWN = 9
    BOMB = 10
    NOBOMB = 11


class MineSweeper:
    def __init__(self,height=0,width=0, fname=None, solutionCap=None):
        self.fname = fname
        self.height = height
        self.width = width
        self.game = GameInstance(self.height, self.width)
        self.solutionCount = 0
        self.solutionCap = 10

    def Frog(self):
        board  = [
            [11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ],
            [11 ,11 ,11 ,11 ,10 ,10 ,10 ,11 ,11 ,11 ,10 ,10 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ],
            [11 ,11 ,11 ,10 ,11 ,11 ,11 ,10 ,11 ,10 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ],
            [11 ,11 ,11 ,10 ,11 ,10 ,11 ,10 ,11 ,10 ,11 ,10 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ],
            [11 ,11 ,11 ,10 ,11 ,10 ,11 ,10 ,10 ,10 ,11 ,10 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ],
            [11 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ],
            [11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ],
            [11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ],
            [11 ,11 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ],
            [11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ],
            [11 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,11 ],
            [11 ,11 ,11 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ],
            [11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ],
            [11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,11 ,10 ,11 ],
            [11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,11 ,10 ,11 ],
            [11 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,10 ,11 ,11 ,11 ,11 ,10 ,11 ],
            [11 ,11 ,11 ,11 ,10 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ,10 ,11 ,11 ,11 ,11 ,11 ,10 ,11 ],
            [11 ,11 ,11 ,11 ,11 ,10 ,10 ,10 ,10 ,10 ,10 ,10 ,11 ,10 ,10 ,10 ,10 ,10 ,11 ,11 ],
            [11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ,11 ]
        ]
        self.height = len(board)
        self.width = len(board[0])
        self.game = GameInstance(self.height, self.width)
        for row in range(self.height):
            for col in range(self.width):
                self.game[0][row][col].state = MSState(board[row][col])

    def createSolutionDir(self):
        try:
            os.mkdir(self.fname)
        except OSError:
            print("Creation of the directory %s failed" % self.fname)
        else:
            print("Successfully created the directory %s " % self.fname)
            self.solutionCount = 0

    def addSolution(self, solution):
        assert isinstance(solution, GameInstance)
        with open(self.fname + '/solution' + str(self.solutionCount) + '.bin', 'wb') as file:
            file.write(solution.toBytes())
        self.solutionCount += 1

    def FillInSequence(self, boundaryCondition=BoundaryCondition.ALL_DEAD):
        sequence = self.game.tilings
        if len(sequence) <= 1:
            raise Exception('A sequence needs at least 2 elements!')
        for tiling in sequence:
            assert isinstance(tiling, Tiling)
            assert tiling.height == sequence[0].height and tiling.width == sequence[0].width, \
                'Cannot compare tilings with different dimensions.'
        oldToNewVariables = dict()
        offsets = [-1, 0, 1]

        inputWires = []
        if DEBUG:
            print('Initiating building of circuit graph.')
            t0 = time.time()
        for index in reversed(range(1, len(sequence))):
            A = sequence[index-1]
            B = sequence[index]
            for row in range(A.height):
                for col in range(A.width):
                    inputWires.append(A[row][col].wire)
                    prevNodes = []
                    for i in offsets:
                        for j in offsets:
                            if boundaryCondition == BoundaryCondition.TOROIDAL:
                                adjustedRow = (row + i) % A.height
                                adjustedCol = (col + j) % A.width
                                prevNodes.append(A[adjustedRow][adjustedCol].wire)
                            elif boundaryCondition == BoundaryCondition.ALL_DEAD:
                                adjustedRow = row + i
                                adjustedCol = col + j
                                # Out of bounds cells count as dead
                                if adjustedRow not in range(A.height) or adjustedCol not in range(A.width):
                                    prevNodes.append(Wire(constant=False))
                                else:
                                    prevNodes.append(A[adjustedRow][adjustedCol].wire)
                            elif boundaryCondition == BoundaryCondition.ALL_ALIVE:
                                adjustedRow = row + i
                                adjustedCol = col + j
                                # Out of bounds cells count as alive
                                if adjustedRow not in range(A.height) or adjustedCol not in range(A.width):
                                    prevNodes.append(Wire(constant=True))
                                else:
                                    prevNodes.append(A[adjustedRow][adjustedCol].wire)
                            else:
                                raise Exception('Unknown boundary condition')
                    tilePrecedingLogic = GateCustom()
                    tilePrecedingLogic.LIFE_nextState(
                        prev9tiles=prevNodes,
                        output=B[row][col].wire)
        if DEBUG:
            total = time.time() - t0
            print('Building of circuit graph completed. (' + str(total) + ' seconds)')
        layerFormula = LogicFormula(inputWires)
        cnfFormula = sorted(layerFormula.cnfForm.rawCNF(),key=lambda x: [len(x), [abs(y) for y in x]])
        cnt = 0
        for tiling in sequence:
            for row in range(tiling.height):
                for col in range(tiling.width):
                    oldToNewVariables[tiling[row][col].variable] = tiling[row][col].wire.variable

        self.createSolutionDir()
        if DEBUG:
            print('Starting to find solutions.')
            t0 = time.time()
        for solution in pycosat.itersolve(cnfFormula):
            if DEBUG and cnt == 0:
                total = time.time() - t0
                print('First solution found in ' + str(total) + ' seconds.')
            if self.solutionCap is not None and self.solutionCap <= cnt:
                break
            # print('--------------------')
            # print(solution)
            updatedSequence = []
            for tiling in sequence:
                newTilingA = Tiling(tiling.height, tiling.width, tiling.time)

                for row in range(tiling.height):
                    for col in range(tiling.width):
                        if oldToNewVariables[tiling[row][col].variable] in solution:
                            if tiling[row][col].state == MSState.ALIVE or tiling[row][col].state == MSState.DONTCARE:
                                # This means that we either forced the cell to be alive or we derived a possible value
                                newTilingA[row][col].state = MSState.ALIVE
                                pass
                            else:
                                raise Exception("Computed state is incompatible with original state")
                        elif -oldToNewVariables[tiling[row][col].variable] in solution:
                            if tiling[row][col].state == MSState.DEAD or tiling[row][col].state == MSState.DONTCARE:
                                # This means that we either forced the cell to be dead or we derived a possible value
                                newTilingA[row][col].state = MSState.DEAD
                                pass
                            else:
                                raise Exception("Computed state is incompatible with original state")
                        else:
                            raise Exception("Input wasn't even in the solution! Something is clearly wrong here.")
                updatedSequence.append(newTilingA)
                # print('After A:')
                # print(newTilingA)
                # print('After B:')
                # print(B)
            gameSolution = GameInstance(boundaryCondition=boundaryCondition)
            gameSolution.SetFrames(updatedSequence)
            print(gameSolution)
            self.addSolution(gameSolution)
            cnt += 1
        if DEBUG:
            total = time.time() - t0
            print('All solutions found or solution limit reached. (' + str(total) + ' seconds)')

    def readSolution(self, fname):
        bytes_read = bytes()
        with open(fname, "rb") as f:
            bytes_read = f.read()
            self.game = GameInstance()
            self.game.loadBytes(bytes_read)


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

    def SetFrames(self, frames):
        if len(frames) == 0:
            raise Exception('Why load in 0 frames?')
        for tiling in frames:
            assert isinstance(tiling, Tiling), 'Frames must be of type Tiling'
            assert tiling.height == frames[0].height and tiling.width == frames[0].width, \
                'Cannot compare tilings with different dimensions.'
        self.tilings = frames
        self.width = frames[0].width
        self.height = frames[0].height

    def loadBytes(self, byteForm):
        numTilings = byteForm[0]
        self.height = byteForm[1]
        self.width = byteForm[2]
        idx = 1
        time = 0
        self.tilings = []
        for tilingIdx in range(numTilings):
            nextIdx = idx + self.height * self.width + 2
            self.tilings.append(Tiling(time=time, byteForm=byteForm[idx:(nextIdx + 1)]))
            idx = nextIdx


    def toBytes(self):
        lstToBytes = bytearray([len(self.tilings)])
        for tiling in self.tilings:
            lstToBytes.extend(tiling.toBytes())
        return bytes(lstToBytes)



class Tiling:
    def __init__(self,height=0,width=0,time=None, byteForm=None):
        self.height = height
        self.width = width
        self.time = time
        if byteForm is not None:
            self.loadBytes(byteForm)
        else:
            self.board = [[Tile(row=y, col=x) for x in range(width)] for y in range(height)]

    def __getitem__(self, key):
        return self.board[key]

    def __str__(self):
        boardStr= ''
        for i in range(self.height):
            for j in range(self.width):
                if self[i][j].state == MSState.ALIVE:
                    boardStr += '■'
                elif self[i][j].state == MSState.DEAD:
                    boardStr += '□'
                elif self[i][j].state == MSState.DONTCARE:
                    boardStr += '▩'
                    # boardStr += str(self[i][j].variable)
                else:
                    raise Exception('Unknown tile state')

            if i != self.width:
                boardStr += '\n'
        return boardStr

    def loadBytes(self, byteForm):
        self.height = byteForm[0]
        self.width = byteForm[1]
        self.board = [[Tile(row=y, col=x) for x in range(self.width)] for y in range(self.height)]
        idx = 2
        for row in range(self.height):
            for col in range(self.width):
                self[row][col].loadBytes(byteForm[idx])
                idx += 1

    def toBytes(self):
        lstToBytes = bytearray([self.height, self.width])
        for row in range(self.height):
            for col in range(self.width):
                lstToBytes.extend(self[row][col].toBytes())
        return lstToBytes


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
                            if self[adjustedRow][adjustedCol].state == MSState.ALIVE and not(i == 0 and j == 0):
                                numAlive += 1
                    # Live cells stay alive when they have 2 or 3 neighbors
                    if self[row][col].state == MSState.ALIVE and (numAlive == 2 or numAlive == 3):
                        newTiling[row][col].state = MSState.ALIVE
                        # Dead cells come alive when they have exactly 3 neighbors
                    elif self[row][col].state == MSState.DEAD and numAlive == 3:
                        newTiling[row][col].state = MSState.ALIVE
                        # All other remaining cells become dead
                    else:
                        newTiling[row][col].state = MSState.DEAD

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
                            elif self[adjustedRow][adjustedCol].state == MSState.ALIVE and not(i == 0 and j == 0):
                                numAlive += 1
                    # Live cells stay alive when they have 2 or 3 neighbors
                    if self[row][col].state == MSState.ALIVE and (numAlive == 2 or numAlive == 3):
                        newTiling[row][col].state = MSState.ALIVE
                        # Dead cells come alive when they have exactly 3 neighbors
                    elif self[row][col].state == MSState.DEAD and numAlive == 3:
                        newTiling[row][col].state = MSState.ALIVE
                        # All other remaining cells become dead
                    else:
                        newTiling[row][col].state = MSState.DEAD

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
                            elif self[adjustedRow][adjustedCol].state == MSState.ALIVE and not(i == 0 and j == 0):
                                numAlive += 1
                    # Live cells stay alive when they have 2 or 3 neighbors
                    if self[row][col].state == MSState.ALIVE and (numAlive == 2 or numAlive == 3):
                        newTiling[row][col].state = MSState.ALIVE
                        # Dead cells come alive when they have exactly 3 neighbors
                    elif self[row][col].state == MSState.DEAD and numAlive == 3:
                        newTiling[row][col].state = MSState.ALIVE
                        # All other remaining cells become dead
                    else:
                        newTiling[row][col].state = MSState.DEAD
        else:
            raise Exception('Unknown boundary condition')
        return newTiling


class Tile:
    def __init__(self, state=MSState.DONTCARE, row=None, col=None, variable=None, time=None):
        self.state = state
        self.row=row
        self.col=col
        self.variable = variable
        self.time = time
        self.wire = Wire(name=str(self))

    def __str__(self):
        return '[' + str(self.row) + ', ' + str(self.col) + ', ' + self.state.name + ']'

    def updateWire(self):
        assert isinstance(self.wire, Wire)
        if self.state == MSState.ALIVE:
            self.wire.constant = True
        elif self.state == MSState.DEAD:
            self.wire.constant = False
        elif self.state == MSState.DONTCARE:
            # reset back to original state
            self.wire.constant = None
        self.wire.name = str(self)

    def loadBytes(self, byteForm):
        self.state = MSState(byteForm)

    def toBytes(self):
        return bytearray([self.state.value])

if __name__ == "__main__":
    test = Testing()
    test.GenerateFrogSolutions()

