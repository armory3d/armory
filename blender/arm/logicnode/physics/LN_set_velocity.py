from arm.logicnode.arm_nodes import *

class SetVelocityNode(ArmLogicTreeNode):
    """Set velocity node"""
    bl_idname = 'LNSetVelocityNode'
    bl_label = 'Set Velocity'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Linear')
        self.add_input('NodeSocketVector', 'Linear Factor', default_value=[1.0, 1.0, 1.0])
        self.add_input('NodeSocketVector', 'Angular')
        self.add_input('NodeSocketVector', 'Angular Factor', default_value=[1.0, 1.0, 1.0])
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetVelocityNode, category=MODULE_AS_CATEGORY)
