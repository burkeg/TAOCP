import adsk.core, adsk.fusion, traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Attempts to coalesce all solids into one object
        DoMerge(app, ui, product, design)

    except:
        if ui:

            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


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
