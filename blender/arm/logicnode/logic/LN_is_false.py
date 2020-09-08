from bpy.types import Node

from arm.logicnode.arm_nodes import *


class IsFalseNode(ArmLogicTreeNode):
    """Is False node"""
    bl_idname = 'LNIsFalseNode'
    bl_label = 'Is False'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')


add_node(IsFalseNode, category=MODULE_AS_CATEGORY)
