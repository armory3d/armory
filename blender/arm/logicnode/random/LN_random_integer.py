from bpy.types import Node
from arm.logicnode.arm_nodes import *


class RandomIntegerNode(ArmLogicTreeNode):
    """Random integer node"""
    bl_idname = 'LNRandomIntegerNode'
    bl_label = 'Random Integer'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('NodeSocketInt', 'Min')
        self.inputs.new('NodeSocketInt', 'Max').default_value = 2
        self.outputs.new('NodeSocketInt', 'Int')


add_node(RandomIntegerNode, category=MODULE_AS_CATEGORY)
