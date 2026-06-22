from arm.logicnode.arm_nodes import *

class ConvexCastOnNode(ArmLogicTreeNode):
    """Casts a convex rigid body and get the closest hit point. Also called Convex Sweep Test.

    @seeNode Mask

    @input In: Input trigger
    @input Convex RB: A convex Rigid Body object to be used for the sweep test.
    @input From: The initial location of the convex object.
    @input To: The final location of the convex object.
    @input Rotation: Rotation of the Convex RB during sweep test.
    @input Mask: A bit mask value to specify which
        objects are considered

    @output Out: Output after hit
    @output Hit Position: The hit position in world coordinates
    @output Convex Position: Position of the convex RB at the time of collision.
    @output Normal: The surface normal of the hit position relative to
        the world.
    """
    bl_idname = 'LNPhysicsConvexCastOnNode'
    bl_label = 'Convex Cast On'
    arm_section = 'ray'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Convex RB')
        self.add_input('ArmVectorSocket', 'From')
        self.add_input('ArmVectorSocket', 'To')
        self.add_input('ArmRotationSocket', 'Rotation')
        self.add_input('ArmIntSocket', 'Mask', default_value=1)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmVectorSocket', 'Hit Position')
        self.add_output('ArmVectorSocket', 'Convex Position')
        self.add_output('ArmVectorSocket', 'Normal')
