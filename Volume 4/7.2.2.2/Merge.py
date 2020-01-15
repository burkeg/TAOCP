import adsk.core, adsk.fusion, traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        root = design.rootComponent

        TargetBody = root.occurrences.item(0).bRepBodies.item(0)

        ToolBodies = adsk.core.ObjectCollection.create()
        beforeCnt = 0
        flag = True
        for occ in root.occurrences:
            for brep in occ.bRepBodies:
                beforeCnt += 1
                if flag:
                    flag = False
                    continue
                ToolBodies.add(brep)
        if beforeCnt == 1:
            ui.messageBox('Only 1 component, nothing to do.')
            return

        CombineInput = root.features.combineFeatures.createInput(TargetBody, ToolBodies)

        CombineFeats = root.features.combineFeatures
        CombineInput = CombineFeats.createInput(TargetBody, ToolBodies)
        CombineInput.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        CombineFeats.add(CombineInput)

        afterCnt = 0
        for occ in root.occurrences:
            for brep in occ.bRepBodies:
                afterCnt += 1

        ui.messageBox(str(beforeCnt) + ' to ' + str(afterCnt) + ' bodies.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
