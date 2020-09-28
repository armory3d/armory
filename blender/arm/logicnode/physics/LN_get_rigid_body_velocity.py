from arm.logicnode.arm_nodes import *

class GetVelocityNode(ArmLogicTreeNode):
    """Get the world velocity of a rigid body."""
    bl_idname = 'LNGetVelocityNode'
    bl_label = 'Get Rigid Body Velocity'
    arm_version = 1

    def init(self, context):
        super(GetVelocityNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_output('NodeSocketVector', 'Linear')
        # self.add_output('NodeSocketVector', 'Linear Factor') # TODO
        # self.outputs[-1].default_value = [1.0, 1.0, 1.0]
        self.add_output('NodeSocketVector', 'Angular')
        # self.add_output('NodeSocketVector', 'Angular Factor') # TODO
        # self.outputs[-1].default_value = [1.0, 1.0, 1.0]

add_node(GetVelocityNode, category=PKG_AS_CATEGORY)
