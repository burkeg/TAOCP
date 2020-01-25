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