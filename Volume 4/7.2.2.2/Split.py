import adsk.core, adsk.fusion, traceback


# numLayers = 6
# expansion = 0.1


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        (numLayers, cancelled) = ui.inputBox('Enter number of layers in design', 'Number of Layers', '5')
        if cancelled:
            return
        else:
            numLayers = int(numLayers)

        (expansion, cancelled) = ui.inputBox('Enter expansion factor', 'expansion factor', '0.1')
        if cancelled:
            return
        else:
            expansion = float(expansion)

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

        ui.messageBox(str(beforeCnt) + ' to ' + str(afterCnt) + ' bodies.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
