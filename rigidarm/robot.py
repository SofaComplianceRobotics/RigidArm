import os
path=os.path.dirname(os.path.abspath(__file__))+'/mesh/'
basePath = path+'RobotBase.stl'
part11Path = path+'RobotPart1.stl'
part12Path = path+'RobotPart3.stl'
part21Path = path+'RobotPart2.stl'
part22Path = path+'RobotPart4.stl'
part3Path = path+'RobotPart6.stl'
part41Path = path+'RobotPart5.stl'
part42Path = path+'RobotPart9.stl'
part51Path = path+'RobotPart7.stl'
part52Path = path+'RobotPart8.stl'
part6Path = path+'RobotPart10.stl'

# # For rendering with Blender
# import utils.animation as animation


def addVisu(node, index, filename, translation=[0, 0, 0]):

    if filename is None:
        return

    visu = node.addChild('Visu'+str(index))
    visu.addObject('MeshSTLLoader', name='loader', filename=filename, translation=translation)
    visu.addObject('MeshTopology', src='@loader')
    visu.addObject('OglModel', color=[1.0,0.8,0.0,1.])
    visu.addObject('RigidMapping')

    return


def addCenter(node, name,
              parentIndex, childIndex,
              posOnParent, posOnChild,
              articulationProcess,
              isTranslation, isRotation, axis,
              articulationIndex):

    center = node.addChild(name)
    center.addObject('ArticulationCenter', parentIndex=parentIndex, childIndex=childIndex, posOnParent=posOnParent, posOnChild=posOnChild, articulationProcess=articulationProcess)

    articulation = center.addChild('Articulation')
    articulation.addObject('Articulation', translation=isTranslation, rotation=isRotation, rotationAxis=axis, articulationIndex=articulationIndex)

    return center


def addPart(node, name, index, filename1, filename2=None, translation=[0, 0, 0]):

    part = node.addChild(name)
    part.addObject('MechanicalObject', template='Rigid3', position=[0,0,0,0,0,0,1])
    part.addObject('RigidMapping', index=index, globalToLocalCoords=True)

    addVisu(part, 1, filename1, translation=translation)
    addVisu(part, 2, filename2, translation=translation)

    return part


class Robot:

    def __init__(self, node):
        self.node = node
        self.robot = None

    def addRequiredPlugins(self):
        if self.robot is not None:
            self.robot.addObject('RequiredPlugin', pluginName=['ArticulatedSystemPlugin' # Needed to use components [ArticulatedHierarchyContainer,ArticulatedSystemMapping,Articulation,ArticulationCenter]  
                                                                ,'Sofa.Component.IO.Mesh' # Needed to use components [MeshSTLLoader]  
                                                                ,'Sofa.Component.Mapping.NonLinear' # Needed to use components [RigidMapping]  
                                                                ,'Sofa.Component.Mass' # Needed to use components [UniformMass]  
                                                                ,'Sofa.Component.StateContainer' # Needed to use components [MechanicalObject]  
                                                                ,'Sofa.Component.Topology.Container.Constant' # Needed to use components [MeshTopology]  
                                                                ,'Sofa.GL.Component.Rendering3D'
                                                                # ,'SofaValidation' # Needed for rendering with Blender
                                                                ]) # Needed to use components [OglModel]  

    def addRobot(self, name='Robot', translation=[0,0,0]):

        # Positions of parts
        positions = [
                    [160.8,     0, 160.8, 0,0,0,1],
                    [160.8,  78.5, 160.8, 0,0,0,1],
                    [254.8,   171, 160.8, 0,0,0,1],
                    [347.3,   372, 160.8, 0,0,0,1],
                    [254.8, 569.6, 160.8, 0,0,0,1],
                    [160.8, 500.5, 160.8, 0,0,0,1],
                    [160.8, 442.5, 160.8, 0,0,0,1]
                    ]

        # Robot node
        robot = self.node.addChild(name)
        self.robot = robot
        self.addRequiredPlugins()

        # Articulations node
        articulations = robot.addChild('Articulations')
        articulations.addObject('MechanicalObject', name='dofs', template='Vec1', 
                                position=[0, 0, 0, 0, 0, 0])
        articulations.addObject('ArticulatedHierarchyContainer')
        articulations.addObject('UniformMass', totalMass=1)

        # Rigid
        rigid = robot.addChild('Rigid')
        rigid.addObject('MechanicalObject', name='dofs', template='Rigid3', showObject=False, showObjectScale=10,
                            position=positions[0:7],
                            translation=translation)
        rigid.addObject('ArticulatedSystemMapping', name="robotArticulatedSystemMapping",
                        input1=articulations.dofs.getLinkPath(), output=rigid.dofs.getLinkPath(),
                        container=articulations.ArticulatedHierarchyContainer.getLinkPath())
        # # For rendering with Blender
        # for i in range(7):
        #     # Add object config for animation
        #     animation.addObjectConfig(node=rigid, 
        #                                 name='RobotPart'+str(i+1), 
        #                                 indices=[i], 
        #                                 template='Rigid3', 
        #                                 objectType='rigid', 
        #                                 meshFilename=[basePath, part11Path, part21Path, part3Path, part41Path, part51Path, part6Path][i])
        #     if i in [1, 2, 4, 5]:  # Parts with two meshes
        #         animation.addObjectConfig(node=rigid, 
        #                                 name='RobotPart2'+str(i+1),
        #                                 indices=[i], 
        #                                 template='Rigid3', 
        #                                 objectType='rigid', 
        #                                 meshFilename=[None, part12Path, part22Path, None, part42Path, part52Path][i])

        # Visu
        visu = rigid.addChild('Visu')
        addPart(visu, 'Base' , 0, basePath, translation=translation)
        addPart(visu, 'Part1', 1, part11Path, part12Path, translation=translation)
        addPart(visu, 'Part2', 2, part21Path, part22Path, translation=translation)
        addPart(visu, 'Part3', 3, part3Path, translation=translation)
        addPart(visu, 'Part4', 4, part41Path, part42Path, translation=translation)
        addPart(visu, 'Part5', 5, part51Path, part52Path, translation=translation)
        addPart(visu, 'Part6', 6, part6Path, translation=translation)

        # Center of articulations
        centers = articulations.addChild('ArticulationsCenters')
        addCenter(centers, 'CenterBase' , 0, 1, [   0,  78.5, 0], [   0,      0, 0], 0, 0, 1, [0, 1, 0], 0)
        addCenter(centers, 'CenterPart1', 1, 2, [  94,  92.5, 0], [   0,      0, 0], 0, 0, 1, [1, 0, 0], 1)
        addCenter(centers, 'CenterPart2', 2, 3, [92.5,  92.5, 0], [   0, -108.5, 0], 0, 0, 1, [0, 1, 0], 2)
        addCenter(centers, 'CenterPart3', 3, 4, [   0, 108.5, 0], [92.5,  -89.1, 0], 0, 0, 1, [0, 0, 0], 3)
        addCenter(centers, 'CenterPart4', 4, 5, [   0,     0, 0], [  94,   69.1, 0], 0, 0, 1, [1, 0, 0], 4)
        addCenter(centers, 'CenterPart5', 5, 6, [   0,     0, 0], [   0,     58, 0], 0, 0, 1, [0, 1, 0], 5)

        return robot


# Test/example scene
def createScene(rootnode):

    from utils.header import addHeader, addSolvers
    import Sofa.ImGui as MyGui
    from math import pi

    settings, modelling, simulation = addHeader(rootnode, inverse=False, withCollision=False, friction=0)

    addSolvers(simulation, rayleighStiffness=0.001)
    rootnode.VisualStyle.displayFlags = ["showVisual"]

    rootnode.dt = 0.001
    rootnode.gravity = [0., -9810., 0.]

    # Robot
    robot = Robot(simulation).addRobot()

    # Direct problem
    for i in range(6):
        joint = robot.Articulations.addObject('JointConstraint', name='joint' + str(i), index=i)
        MyGui.MyRobotWindow.Settings.addData("Joint" + str(i), joint.value, -pi, pi)

    return