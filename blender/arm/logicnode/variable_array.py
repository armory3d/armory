import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayNode(Node, ArmLogicTreeNode):
    '''Array node'''
    bl_idname = 'LNArrayNode'
    bl_label = 'Array'
    bl_icon = 'GAME'
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Array")
        self.outputs.new('NodeSocketInt', "Length")

add_node(ArrayNode, category='Variable')
