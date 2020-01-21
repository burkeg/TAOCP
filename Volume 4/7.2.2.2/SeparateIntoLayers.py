# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = product
        layerCnt = 6
        expansion = 0.1
        SeparateIntoLayers(app, ui, product, design, layerCnt, expansion)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def SeparateIntoLayers(app, ui, product, design, layerCnt, expansion):
    # Get the root component of the active design
    root = design.rootComponent

    ToolBodies = adsk.core.ObjectCollection.create()

    # CombineInput = root.features.combineFeatures.createInput(TargetBody, ToolBodies)

    # CombineFeats = root.features.combineFeatures
    # CombineInput = CombineFeats.createInput(TargetBody, ToolBodies)
    # CombineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    # CombineFeats.add(CombineInput)

    # afterCnt = 0
    # for occ in root.occurrences:
    #     for brep in occ.bRepBodies:
    #         afterCnt += 1
    layers = []
    for i in range(layerCnt):
        layers.append(makeLayer(i, design))
    for occ in root.occurrences:
        for brep in occ.bRepBodies:
            assert isinstance(brep, adsk.fusion.BRepBody)
            print(brep.boundingBox.maxPoint.z)
            layer = layers[zToLayer(brep.boundingBox.maxPoint.z, expansion)]
            assert isinstance(layer, adsk.fusion.Component)
            layer.bRepBodies.add(brep)


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