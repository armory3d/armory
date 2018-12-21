import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RandomFloatNode(Node, ArmLogicTreeNode):
    '''Random float node'''
    bl_idname = 'LNRandomFloatNode'
    bl_label = 'Random (Float)'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Min')
        self.inputs.new('NodeSocketFloat', 'Max')
        self.inputs[-1].default_value = 1.0
        # self.inputs.new('NodeSocketInt', 'Seed')
        self.outputs.new('NodeSocketFloat', 'Float')

add_node(RandomFloatNode, category='Value')
