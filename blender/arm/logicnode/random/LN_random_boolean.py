from bpy.types import Node
from arm.logicnode.arm_nodes import *


class RandomBooleanNode(Node, ArmLogicTreeNode):
    """Random boolean node"""
    bl_idname = 'LNRandomBooleanNode'
    bl_label = 'Random Boolean'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketBool', 'Bool')


add_node(RandomBooleanNode, category=MODULE_AS_CATEGORY)
