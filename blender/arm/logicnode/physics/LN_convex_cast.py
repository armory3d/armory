from arm.logicnode.arm_nodes import *

class ConvexCastNode(ArmLogicTreeNode):
    """Casts a convex rigid body and get the closest hit point.

    @seeNode Mask

    @input From: The initial transform of the convex object. Only location and rotation are considered.
    @input To: The final transform of the convex object. Only location and rotation are considered.
    @input Mask: a bit mask value to specify which
        objects are considered

    @output Hit: the hit position in world coordinates
    @output Normal: the surface normal of the hit position relative to
        the world
    """
    bl_idname = 'LNPhysicsConvexCastNode'
    bl_label = 'Convex Cast'
    arm_section = 'ray'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Convex RB')
        self.add_input('ArmDynamicSocket', 'From')
        self.add_input('ArmDynamicSocket', 'To')
        self.add_input('ArmIntSocket', 'Mask', default_value=1)

        self.add_output('ArmVectorSocket', 'Hit')
        self.add_output('ArmVectorSocket', 'Normal')
