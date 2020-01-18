# Author-
# Description-

import adsk.core, adsk.fusion, traceback

expansion = 0.1


def main():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = product

        fileDialog = ui.createFileDialog()
        fileDialog.initialDirectory = r"C:\Users\Gabri\Documents\gitRepos\TAOCP\Volume 4\7.2.2.2"
        fileDialog.isMultiSelectEnabled = False
        fileDialog.title = "Select Game of Life binary to construct"
        fileDialog.filter = 'Binary files (*.bin)'
        fileDialog.filterIndex = 0
        dialogResult = fileDialog.showOpen()
        if dialogResult == adsk.core.DialogResults.DialogOK:
            path = fileDialog.filename
        else:
            return
        global expansion
        (expansion, cancelled) = ui.inputBox('Enter expansion factor', 'expansion factor', str(expansion))
        if cancelled:
            return
        else:
            expansion = float(expansion)

        lg = Life()
        lg.readSolution(path)
        LifeSTL(lg, render=False, des=design)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def drawCubes(design, argList):
    # Get reference to the root component
    rootComp = design.rootComponent

    # Create a new component
    occurrence = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component
    # Name the component
    component.name = "Layer"

    # coordinates = [
    #     0,0,0,
    #     2,0,0,
    #     1,1,0,
    #     0,1,0,
    #     0,0,0
    # ]
    for flCorner, expansion in argList:
        x = flCorner[0]
        y = flCorner[1]
        z = flCorner[2]
        xm = x - expansion
        ym = y - expansion
        zm = z - expansion
        xp = x + expansion + 1
        yp = y + expansion + 1
        zp = z + expansion + 1
        coordinates = [
            xm, ym, zm,
            xp, ym, zm,
            xp, yp, zm,
            xm, yp, zm,
            xm, ym, zm
        ]

        # Get reference to the sketchs and plane
        sketches = component.sketches
        xyPlane = component.xYConstructionPlane

        # Create a new sketch and get lines reference
        sketch = sketches.add(xyPlane)
        lines = sketch.sketchCurves.sketchLines
        i = 0
        while i < len(coordinates) - 3:
            point1 = adsk.core.Point3D.create(coordinates[i], coordinates[i + 1], coordinates[i + 2])
            point2 = adsk.core.Point3D.create(coordinates[i + 3], coordinates[i + 4], coordinates[i + 5])
            # Create Line
            lines.addByTwoPoints(point1, point2)
            i += 3

        # Get reference to the first profile of the sketch
        profile = sketch.profiles.item(sketch.profiles.count - 1)

        # Get extrude features reference
        extrudes = component.features.extrudeFeatures

        # Create input object for the extrude feature
        extInput = extrudes.createInput(profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(1 + 2 * expansion)
        extInput.setDistanceExtent(False, distance)

        # Create extrusion
        extrudes.add(extInput)


#

# ----------------------------------------------------------------------
# from stl import mesh
# import math
# import numpy
import os


# import copy
# from Life import Life, LifeTiling, LifeState
# import numpy as np
# from matplotlib import pyplot
# from mpl_toolkits import mplot3d


class LifeSTL:
    def __init__(self, lifeGame, render=True, des=None):
        assert isinstance(lifeGame, Life)
        self.lifeGame = lifeGame
        self.meshes = []
        self.convertLifeToStlSquare(des)

    def convertLifeToStlSquare(self, des):
        cubesInLayer = []
        for i, tiling in enumerate(self.lifeGame.game.tilings):
            assert isinstance(tiling, LifeTiling)
            for row in range(tiling.height):
                for col in range(tiling.width):
                    if tiling[row][col].state == LifeState.ALIVE:
                        cubesInLayer.append(((row, col, i), expansion))
            # break
        drawCubes(des, cubesInLayer)
        print(cubesInLayer)


# --------------------------------------------------------
# import pycosat
# import math
# import numpy as np
# import pprint as pp
# import sys
# import collections
# import re
# import time
# import os

# from SATUtils import SATUtils, CNF, Clause, Literal, DSAT, Tseytin
# from LogicFormula import *
from enum import Enum


# from collections import namedtuple
# from GraphColoring import GraphColoring

class LifeState(Enum):
    ALIVE = 0
    DEAD = 1
    DONTCARE = 2


class BoundaryCondition(Enum):
    TOROIDAL = 0
    ALL_DEAD = 1
    ALL_ALIVE = 2


class Life:
    def __init__(self, height=0, width=0, fname=None, solutionCap=None):
        self.fname = fname
        self.height = height
        self.width = width
        self.game = LifeGameInstance(self.height, self.width)
        self.solutionCount = 0
        self.solutionCap = 10

    def readSolution(self, fname):
        bytes_read = bytes()
        with open(fname, "rb") as f:
            bytes_read = f.read()
            self.game = LifeGameInstance()
            self.game.loadBytes(bytes_read)


class LifeGameInstance:
    def __init__(self, height=0, width=0, boundaryCondition=BoundaryCondition.TOROIDAL):
        self.height = height
        self.width = width
        self.boundaryCondition = boundaryCondition
        self.tilings = [LifeTiling(height=height, width=width, time=0)]

    def __getitem__(self, key):
        return self.tilings[key]

    def __str__(self):
        gameStr = '-------------\n'
        for t in range(len(self.tilings)):
            gameStr += 'Time = ' + str(t) + '\n'
            gameStr += str(self[t])
            gameStr += '-------------\n'
        return gameStr

    def loadBytes(self, byteForm):
        numTilings = byteForm[0]
        self.height = byteForm[1]
        self.width = byteForm[2]
        idx = 1
        time = 0
        self.tilings = []
        for tilingIdx in range(numTilings):
            nextIdx = idx + self.height * self.width + 2
            self.tilings.append(LifeTiling(time=time, byteForm=byteForm[idx:(nextIdx + 1)]))
            idx = nextIdx


class LifeTiling:
    def __init__(self, height=0, width=0, time=None, byteForm=None):
        self.height = height
        self.width = width
        self.time = time
        if byteForm is not None:
            self.loadBytes(byteForm)
        else:
            self.board = [[LifeTile(row=y, col=x) for x in range(width)] for y in range(height)]

    def __getitem__(self, key):
        return self.board[key]

    def __str__(self):
        boardStr = ''
        for i in range(self.height):
            for j in range(self.width):
                if self[i][j].state == LifeState.ALIVE:
                    boardStr += '■'
                elif self[i][j].state == LifeState.DEAD:
                    boardStr += '□'
                elif self[i][j].state == LifeState.DONTCARE:
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
        self.board = [[LifeTile(row=y, col=x) for x in range(self.width)] for y in range(self.height)]
        idx = 2
        for row in range(self.height):
            for col in range(self.width):
                self[row][col].loadBytes(byteForm[idx])
                idx += 1


class LifeTile:
    def __init__(self, state=LifeState.DONTCARE, row=None, col=None, variable=None, time=None):
        assert issubclass(type(state), Enum)
        self.state = state
        self.row = row
        self.col = col
        self.variable = variable
        self.time = time
        self.wire = Wire(name=str(self))

    def __str__(self):
        return '[' + str(self.row) + ', ' + str(self.col) + ', ' + self.state.name + ']'

    def loadBytes(self, byteForm):
        self.state = LifeState(byteForm)


# ----------------------------------------------------------------------------------------------


class Wire:
    def __init__(self, gateOut=None, gatesIn=None, variable=None, constant=None, name=None):
        self.variable = variable
        if gatesIn is None:
            self.gatesIn = []
        self.gateOut = gateOut
        self.constant = constant
        self.name = name


main()

