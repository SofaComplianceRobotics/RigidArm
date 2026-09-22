class Robot:

    def __init__(self, node):
        self.node = node
        self.robot = None

    def addRobot(self, name='Robot', filename="mesh/robot.urdf", modelDirectory="mesh/"):

        # Robot node
        self.node.addObject("RequiredPlugin", name=name+"RequiredPlugins",
                             pluginName=["Sofa.RigidBodyDynamics" # Needed to use components [URDFModelLoader]
                                        ,'Sofa.Component.Mapping.NonLinear' # Needed to use components [RigidMapping]  
                                        ,'Sofa.Component.Mass' # Needed to use components [UniformMass]
                                        ,'Sofa.Component.Topology.Container.Constant' # Needed to use components [MeshTopology]  
                                        ,'Sofa.Component.SolidMechanics.Spring'
                                        ,'Sofa.Component.StateContainer'
                                        ,'Sofa.GL.Component.Rendering3D']) # Needed to use components [OglModel]  

        self.node.addObject('URDFModelLoader', 
                            filename=filename, 
                            modelDirectory=modelDirectory, 
                            useFreeFlyerRootJoint=False, 
                            printLog=False, 
                            addCollision=False, 
                            addJointsActuators=False)
        robot = self.node.getChild(name)
        mechanical = robot.Model.getMechanicalState()
        mechanical.showObject = True
        mechanical.showObjectScale = 30
        mechanical.drawMode = 0

        self.robot = robot
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
        joint = robot.addObject('JointConstraint', template='Vec1', name='joint' + str(i), index=i)
        MyGui.MyRobotWindow.Settings.addData("Joint" + str(i), joint.value, -pi, pi)
    robot.addObject("RestShapeSpringsForceField", points=[3], stiffness=1e12)

    return
