# Author-
# Description-

import adsk.core, adsk.fusion, traceback


def main():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = product
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    drawCube(design, (i, j, k), 0.2)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def drawCube(design, flCorner, expansion):
    # Get reference to the root component
    rootComp = design.rootComponent

    # Create a new component
    occurrence = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component

    # coordinates = [
    #     0,0,0,
    #     2,0,0,
    #     1,1,0,
    #     0,1,0,
    #     0,0,0
    # ]
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
    # Name the component
    component.name = "Cube"

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


main()

