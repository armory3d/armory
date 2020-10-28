from arm.logicnode.arm_nodes import *

class GetVelocityNode(ArmLogicTreeNode):
    """Returns the world velocity of the given rigid body."""
    bl_idname = 'LNGetVelocityNode'
    bl_label = 'Get RB Velocity'
    arm_version = 1

    def init(self, context):
        super(GetVelocityNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_output('NodeSocketVector', 'Linear')
        self.add_output('NodeSocketVector', 'Angular')
