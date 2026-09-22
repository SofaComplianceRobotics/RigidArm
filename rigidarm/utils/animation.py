import toml
import os
import Sofa

# Utils to render the animation in Blender
# We use the script `blender_importer.py` from `https://gitlab.inria.fr/imagine_rennes/blender_toolbox`
# to set up the animation in Blender. This script (`blender_importer.py`) takes a toml file as input.
# See blender_importer.example.toml

outputDir: str = '/tmp/last_sofa_run/'

blenderAnimationConfig = {
        'frames': 2500,
        'frequency': 1,
        'objects': []
    }


# Adds the toml description of a given object to the static params.scene.blenderAnimationConfig
def addObjectConfig(node, name, indices, template, objectType, meshFilename,
                    translation=[0, 0, 0], rotation=[0, 0, 0], scale=[1, 1, 1]):

    extension = ''
    path = "/home/eulalie/Softs/SOFA/project/Emio.CND/mesh/" + meshFilename
    if not os.path.exists(path + extension):
        path = meshFilename
        if not os.path.exists(path + extension):
            Sofa.msg_error("Mesh file path does not exist: ", "/home/eulalie/Softs/SOFA/project/Emio.CND/mesh/" + meshFilename + extension)
            Sofa.msg_error("Mesh file path does not exist: ", meshFilename + extension)
            return

    objectConfig = {
        'mesh': path,
        'type': objectType,
        'name': name,
        'scale': [float(s) for s in scale]
    }

    if objectType == 'static':  # no animation
        objectConfig['translation'] = [float(t) for t in translation]
        objectConfig['rotation'] = [float(r) for r in rotation]

    objectConfig['monitor'] = '/tmp/last_sofa_run/' + name + '_x.txt'
    blenderAnimationConfig['objects'].append(objectConfig)
    node.addObject('Monitor', name="monitor"+name, template=template, listening=True, ExportPositions=True,
                   ExportVelocities=False,
                   ExportForces=False, indices=indices, fileName=outputDir + name)


# Export params.scene.blenderAnimationConfig
def exportAnimationConfig(filename):

    with open(filename, 'w+') as f:
        toml.dump(blenderAnimationConfig, f)
