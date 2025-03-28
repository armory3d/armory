from arm.logicnode.arm_nodes import *

class GetPointVelocityNode(ArmLogicTreeNode):
    """Returns the world velocity of the given point along the rigid body."""
    bl_idname = 'LNGetPointVelocityNode'
    bl_label = 'Get RB Point Velocity'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmVectorSocket', 'Point')

        self.add_output('ArmVectorSocket', 'Velocity')
