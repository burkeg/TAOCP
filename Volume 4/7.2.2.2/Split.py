import adsk.core, adsk.fusion, traceback

filename = ''

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design
        root = design.rootComponent
        rootComp = root
        SplitBodies = adsk.core.ObjectCollection.create()
        for occ in root.occurrences:
            for brep in occ.bRepBodies:
                SplitBodies.add(brep)

        # Save the file as STL.
        exportMgr = adsk.fusion.ExportManager.cast(design.exportManager)
        stlOptions = exportMgr.createSTLExportOptions(rootComp)
        stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementMedium
        stlOptions.filename = filename
        exportMgr.execute(stlOptions)
        ui.messageBox('Done!')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
