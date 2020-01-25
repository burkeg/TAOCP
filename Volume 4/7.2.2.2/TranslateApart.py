# Author-
# Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import math
import re


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = product
        expansion = 0.1
        TranslateApart(app, ui, product, design, expansion)

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
        vector = adsk.core.Vector3D.create(0.0, 0.0, float(i))
        transform = adsk.core.Matrix3D.create()
        transform.translation = vector

        # Create a move feature
        moveFeats = features.moveFeatures
        TranslateBody(root, moveFeats, occ.component, transform)


def TranslateBody(root, moveFeats, origComponent, transform):
    for body in origComponent.bRepBodies:
        # Cut/paste body from component to root
        cutPasteBody = root.features.cutPasteBodies.add(body)

        # Create a collection of entities for move
        bodies = adsk.core.ObjectCollection.create()
        for k in range(root.bRepBodies.count):
            bodies.add(root.bRepBodies.item(k))

        moveFeatureInput = moveFeats.createInput(bodies, transform)
        moveFeats.add(moveFeatureInput)

        for bodyRoot in root.bRepBodies:
            # Cut/paste body from component to root
            cutPasteBody = origComponent.features.cutPasteBodies.add(bodyRoot)
