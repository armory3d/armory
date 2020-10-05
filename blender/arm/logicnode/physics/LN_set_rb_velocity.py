from arm.logicnode.arm_nodes import *

class SetVelocityNode(ArmLogicTreeNode):
    """Sets the velocity of the given rigid body."""
    bl_idname = 'LNSetVelocityNode'
    bl_label = 'Set RB Velocity'
    arm_version = 1

    def init(self, context):
        super(SetVelocityNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('NodeSocketVector', 'Linear')
        self.add_input('NodeSocketVector', 'Linear Factor', default_value=[1.0, 1.0, 1.0])
        self.add_input('NodeSocketVector', 'Angular')
        self.add_input('NodeSocketVector', 'Angular Factor', default_value=[1.0, 1.0, 1.0])
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetVelocityNode, category=PKG_AS_CATEGORY)
