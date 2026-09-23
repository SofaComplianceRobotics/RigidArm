from math import pi
import numpy as np
import Sofa.SofaConstraintSolver
import Sofa.SoftRobotsInverse
import Sofa.SoftRobots
    

def createScene(rootnode):
    from splib3.animation import AnimationManager, animate
    import Sofa.ImGui as MyGui
    from rigidarm.utils.header import addHeader, addSolvers
    from rigidarm.robot_pinocchio import Robot

    INVERSE = True # Set to True for inverse problem, False for direct problem

    settings, modelling, simulation = addHeader(rootnode, inverse=INVERSE)

    if INVERSE:
        rootnode.ConstraintSolver.epsilon=1e-6
    addSolvers(simulation, firstOrder=1)
    rootnode.addObject(AnimationManager(rootnode))
    rootnode.VisualStyle.displayFlags = ["showVisual"]

    rootnode.dt = 0.001
    rootnode.gravity = [0., -9810., 0.]

    # Robot
    robot = Robot(simulation).addRobot(filename="rigidarm/mesh/robot.urdf", modelDirectory="rigidarm/mesh/")

    if INVERSE: # Inverse problem
        
        targetPosition = [0., 450., 0., 0., 0., 0., 1.]

        # Target
        target = modelling.addChild('EffectorTarget')
        target.addObject('EulerImplicitSolver', firstOrder=True)
        target.addObject('CGLinearSolver', iterations=100, threshold=1e-2, tolerance=1e-5)
        target.addObject('MechanicalObject', template='Rigid3',
                          position=[targetPosition],
                          showObject=True, drawMode=0, showObjectScale=50)

        # Effector
        effector = robot.Joints.addChild("Effector")
        effector.addObject("MechanicalObject", template='Rigid3', position=[[0, 0, 0, 0, 0, 0, 1]])
        effector.addObject('PositionEffector', name='effectorposition', template='Rigid3', indices=[0],
                            effectorGoal=target.getMechanicalState().position.linkpath,
                            useDirections=[1, 1, 1, 1, 1, 1],
                            weight=[1, 1, 1, 100, 100, 100])
        effector.addObject("RigidMapping", index=6)

        robot.addObject("RestShapeSpringsForceField", points=[3], stiffness=1e12)

        # GUI sliders and JointActuators for the inverse problem
        MyGui.setInverseProblemSolver(rootnode.ConstraintSolver)
        MyGui.addTCP("TCP", effector.effectorposition, -500, 500)
        for i in range(6):
            joint = robot.addObject('JointActuator', template='Vec1', name='joint' + str(i), index=i, maxAngleVariation=0.01)
            MyGui.addActuator("M"+str(i), joint, -pi, pi)

        # Target animation
        def animation(target, endPosition, startPosition, factor, startTime=0):
            if factor > 0:
                q = [0, 0, 0, 0, 0, 0, 0]
                # Allow for acceleration and deceleration by using a trigonometric function
                for i in range(7):
                    q[i] = startPosition[i] + (endPosition[i] - startPosition[i]) * (0.5 - 0.5 * np.cos(np.pi * factor))
                # Normalize quaternion
                q[3:7] /= np.linalg.norm(q[3:7])
                target.value = [np.copy(q)]

        # Initial position of the target
        startTime = 0.
        duration = 0.5
        startPosition = np.copy(targetPosition)
        endPosition = [0., 700., 300., 1., 0., 0., 0.]
        animate(animation, {'target': target.getMechanicalState().position, 
                            'endPosition': endPosition, 
                            'startPosition': startPosition,
                            'startTime': startTime}, duration=duration)

        # Pick and place animation
        startTime += duration
        duration = 0.5
        startPosition = np.copy(endPosition)
        endPosition = [0., 700., -300., 1., 0., 0., 0.]
        animate(animation, {'target': target.getMechanicalState().position,
                            'endPosition': endPosition,
                            'startPosition': startPosition,
                            'startTime': startTime}, duration=duration, mode="pingpong")

    else: # Direct problem
        
        for i in range(6):
            joint = robot.Articulations.addObject('JointConstraint', template='Vec1', name='joint' + str(i), index=i)
            MyGui.MyRobotWindow.Settings.addData("Joint" + str(i), joint.value, -pi, pi)

    return 
