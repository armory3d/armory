from bpy.types import Node
from arm.logicnode.arm_nodes import *


class IsNoneNode(Node, ArmLogicTreeNode):
    """Is none node"""
    bl_idname = 'LNIsNoneNode'
    bl_label = 'Is None'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')


add_node(IsNoneNode, category=MODULE_AS_CATEGORY)
