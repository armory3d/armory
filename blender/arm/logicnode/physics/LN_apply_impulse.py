from arm.logicnode.arm_nodes import *

class ApplyImpulseNode(ArmLogicTreeNode):
    """Apply impulse node"""
    bl_idname = 'LNApplyImpulseNode'
    bl_label = 'Apply Impulse'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Impulse')
        self.add_input('NodeSocketBool', 'On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyImpulseNode, category=MODULE_AS_CATEGORY, section='force')
