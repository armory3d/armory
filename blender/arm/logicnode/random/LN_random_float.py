from bpy.types import Node
from arm.logicnode.arm_nodes import *


class RandomFloatNode(ArmLogicTreeNode):
    """Random float node"""
    bl_idname = 'LNRandomFloatNode'
    bl_label = 'Random Float'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Min')
        self.inputs.new('NodeSocketFloat', 'Max').default_value = 1.0
        # self.inputs.new('NodeSocketInt', 'Seed')
        self.outputs.new('NodeSocketFloat', 'Float')


add_node(RandomFloatNode, category=MODULE_AS_CATEGORY)
