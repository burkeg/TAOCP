import adsk.core, adsk.fusion, traceback
import os

# folder = os.path.dirname(os.path.abspath(__file__)) + r'\STL_Output'
folder = r'c:\TEMP\STL_Output'


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        exportCompBodyAsSTL(app, ui, product, design)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# https://forums.autodesk.com/t5/fusion-360-api-and-scripts/python-api-export-stl-from-brepbody-fails/td-p/6299830
def exportCompBodyAsSTL(app, ui, product, design):
    root = design.rootComponent
    exportMgr = design.exportManager
    if not os.path.exists(folder):
        os.makedirs(folder)
    # outDir = r'C:\Users\Gabri\Documents\gitRepos\TAOCP\Volume 4\7.2.2.2\STL_Export'
    for comp in design.allComponents:
        if comp != root:
            # Find any occurrence using this component.
            occs = root.allOccurrencesByComponent(comp)
            if occs.count > 0:
                occ = occs.item(0)

        for body in comp.bRepBodies:
            if comp != root:
                # Create a body proxy.
                body = body.createForAssemblyContext(occ)

            fileName = folder + '\\' + comp.name.replace(" ", "_") + body.name
            print(fileName)
            # create stl exportOptions
            stlExportOptions = exportMgr.createSTLExportOptions(body, fileName)
            stlExportOptions.sendToPrintUtility = False

            exportMgr.execute(stlExportOptions)