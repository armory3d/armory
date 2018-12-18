import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RandomIntegerNode(Node, ArmLogicTreeNode):
    '''Random integer node'''
    bl_idname = 'LNRandomIntegerNode'
    bl_label = 'Random (Integer)'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketInt', 'Min')
        self.inputs.new('NodeSocketInt', 'Max')
        self.inputs[-1].default_value = 2
        self.outputs.new('NodeSocketInt', 'Int')

add_node(RandomIntegerNode, category='Value')
