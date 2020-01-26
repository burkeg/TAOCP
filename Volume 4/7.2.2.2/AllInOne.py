# Author-
# Description-

import adsk.core, adsk.fusion, traceback
import math
import re

expansion = 0.1


def main():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = product

        # Generates solid cubes according to LIFE board states
        layerCnt, expansion = MakeSolid(app, ui, product, design)

        # Attempts to coalesce all solids into one object
        DoMerge(app, ui, product, design)

        # Cuts apart the design into layers by slicing just under each overhang
        SplitIntoLayers(app, ui, product, design, layerCnt, expansion)

        # Reorganizes bodies into separate components for each printable layer
        SeparateIntoLayers(app, ui, product, design, layerCnt, expansion)
        # SeparateIntoLayers(app, ui, product, design, 4, 0.1)

        # Physically move each of the layers apart slightly
        TranslateApart(app, ui, product, design, expansion)

        # Remerge so that pointless components that were split earlier go away
        DoMerge(app, ui, product, design)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def TranslateApart(app, ui, product, design, expansion):
    # Get the root component of the active design
    root = design.rootComponent
    rootComp = design.rootComponent
    features = rootComp.features

    assert isinstance(root, adsk.fusion.Component)
    for occ in root.occurrences:
        assert isinstance(occ, adsk.fusion.Occurrence)
        m = re.match(r'Layer (\d)+:\d+', occ.name)
        if not m:
            continue
        i = int(m.group(1))
        # Create a transform to do move
        vector = adsk.core.Vector3D.create(0.0, 0.0, 3*float(i))
        transform = adsk.core.Matrix3D.create()
        transform.translation = vector

        # Create a move feature
        moveFeats = features.moveFeatures
        TranslateBody(occ.component, transform)


def TranslateBody(origComponent, transform):
    moveFeats = origComponent.features.moveFeatures
    # Create a collection of entities for move
    bodies = adsk.core.ObjectCollection.create()
    for k in range(origComponent.bRepBodies.count):
        bodies.add(origComponent.bRepBodies.item(k))

    moveFeatureInput = moveFeats.createInput(bodies, transform)
    moveFeats.add(moveFeatureInput)

def SeparateIntoLayers(app, ui, product, design, layerCnt, expansion):
    # Get the root component of the active design
    root = design.rootComponent

    ToolBodies = adsk.core.ObjectCollection.create()
    layers = []
    for i in range(layerCnt):
        layers.append(makeLayer(i, design))
    origCompLst = []
    for occ in [x for x in root.occurrences]:
        origCompLst.append((occ.component, [x for x in occ.component.bRepBodies]))

    for comp, bodies in origCompLst:
        test = 0
        for body in bodies:
            assert isinstance(body, adsk.fusion.BRepBody)
            print(body.boundingBox.maxPoint.z)
            layer = layers[zToLayer(body.boundingBox.maxPoint.z, expansion)]
            assert isinstance(layer, adsk.fusion.Component)
            # Cut/paste body from sub component 1 to sub component 2
            cutPasteBody = layer.features.cutPasteBodies.add(body)

def zToLayer(z, expansion):
    adjZ = z - expansion
    i = math.floor(adjZ)
    if math.isclose(adjZ, i):
        return i - 1
    else:
        return i

def makeLayer(i, design):
    # Create a new component
    occurrence = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component
    # Name the component
    if i != 0:
        component.name = "Layer " + str(i)
    else:
        component.name = "Base"
    return component

def SplitIntoLayers(app, ui, product, design, layerCnt, expansion):
    # (numLayers, cancelled) = ui.inputBox('Enter number of layers in design', 'Number of Layers', '5')
    # if cancelled:
    #     return
    # else:
    #     numLayers = int(numLayers)
    numLayers = layerCnt
    # (expansion, cancelled) = ui.inputBox('Enter expansion factor', 'expansion factor', '0.1')
    # if cancelled:
    #     return
    # else:
    #     expansion = float(expansion)

    # Get the root component of the active design
    root = design.rootComponent
    rootComp = root
    beforeCnt = 0
    for occ in root.occurrences:
        for brep in occ.bRepBodies:
            beforeCnt += 1

    for i in range(numLayers - 1):

        TargetBody = root.occurrences.item(0).bRepBodies.item(0)

        SplitBodies = adsk.core.ObjectCollection.create()
        flag = True
        for occ in root.occurrences:
            for brep in occ.bRepBodies:
                if flag:
                    flag = False
                SplitBodies.add(brep)
        # if beforeCnt == 1:
        #     ui.messageBox('Only 1 component, nothing to do.')
        #     return

        # Create sketch
        sketches = rootComp.sketches
        sketch = sketches.add(rootComp.xYConstructionPlane)

        # Get construction planes
        planes = rootComp.constructionPlanes

        # Create construction plane input
        planeInput = planes.createInput()

        # Add construction plane by offset
        offsetValue = adsk.core.ValueInput.createByReal(i + 1 - expansion)
        planeInput.setByOffset(sketch.referencePlane, offsetValue)
        planeOne = planes.add(planeInput)

        # Get the health state of the plane
        health = planeOne.healthState
        if health == adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState or health == adsk.fusion.FeatureHealthStates.WarningFeatureHealthState:
            message = planeOne.errorOrWarningMessage
            # splitBodies, splittingTool, isSplittingToolExtended
        # SplitInput = root.features.splitBodyFeatures.createInput(SplitBodies, planeOne, True)

        # # CombineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        # SplitInput.operation = adsk.fusion.FeatureOperations.SplitBodies
        # root.features.splitBodyFeatures.add(SplitInput)
        # -----
        splitBodyFeats = rootComp.features.splitBodyFeatures
        splitBodyInput = splitBodyFeats.createInput(SplitBodies, planeOne, True)
        # Create split body feature
        splitBodyFeats.add(splitBodyInput)
    afterCnt = 0
    for occ in root.occurrences:
        for brep in occ.bRepBodies:
            afterCnt += 1

    # ui.messageBox(str(beforeCnt) + ' to ' + str(afterCnt) + ' bodies.')

def MakeSolid(app, ui, product, design):
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

    # Create a new component
    occurrence = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component
    # Name the component
    component.name = "Life"
    lg = Life()
    lg.readSolution(path)
    drawBase(design, (lg.game.height, lg.game.width), component, baseThickness=0.5)
    LifeSTL(lg, render=False, des=design, component=component)
    return len(lg.game.tilings), expansion


def DoMerge(app, ui, product, design):
    # Get the root component of the active design
    root = design.rootComponent
    MergeComponent(app, ui, product, design, root)
    for occ in root.occurrences:
        MergeComponent(app, ui, product, design, occ.component)


def MergeComponent(app, ui, product, design, component):
    assert isinstance(component, adsk.fusion.Component)
    if component.bRepBodies.count <= 1:
        # No need to merge 0 or 1 bodies
        return
    TargetBody = component.bRepBodies.item(0)

    ToolBodies = adsk.core.ObjectCollection.create()
    beforeCnt = 0
    flag = True
    for k in range(1, component.bRepBodies.count):
        ToolBodies.add(component.bRepBodies.item(k))

    CombineInput = component.features.combineFeatures.createInput(TargetBody, ToolBodies)

    CombineFeats = component.features.combineFeatures
    CombineInput = CombineFeats.createInput(TargetBody, ToolBodies)
    CombineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CombineFeats.add(CombineInput)


def drawBase(design, dimensions, component, baseThickness=1.0):
    # Get reference to the root component
    rootComp = design.rootComponent

    # coordinates = [
    #     0,0,0,
    #     2,0,0,
    #     1,1,0,
    #     0,1,0,
    #     0,0,0
    # ]
    x = -1
    y = -1
    z = -expansion - baseThickness
    xm = x
    ym = y
    zm = z
    xp = dimensions[0] + 1
    yp = dimensions[1] + 1
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
    distance = adsk.core.ValueInput.createByReal(baseThickness)
    extInput.setDistanceExtent(False, distance)

    # Create extrusion
    extrudes.add(extInput)


def drawCubes(design, argList, component):
    # Get reference to the root component
    rootComp = design.rootComponent

    # # Create a new component
    # occurrence = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    # component = occurrence.component
    # # Name the component
    # component.name = "Layer"

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
    def __init__(self, lifeGame, component, render=True, des=None):
        assert isinstance(lifeGame, Life)
        self.lifeGame = lifeGame
        self.meshes = []
        self.convertLifeToStlSquare(des, component)

    def convertLifeToStlSquare(self, des, component):
        cubesInLayer = []
        for i, tiling in enumerate(self.lifeGame.game.tilings):
            assert isinstance(tiling, LifeTiling)
            for row in range(tiling.height):
                for col in range(tiling.width):
                    if tiling[row][col].state == LifeState.ALIVE:
                        cubesInLayer.append(((row, col, i), expansion))
            # break
        drawCubes(des, cubesInLayer, component)
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

