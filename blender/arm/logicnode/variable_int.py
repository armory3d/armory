import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IntNode(Node, ArmLogicTreeNode):
    '''Int node'''
    bl_idname = 'IntNodeType'
    bl_label = 'Int'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketInt', "Value")
        self.outputs.new('NodeSocketInt', "Int")

add_node(IntNode, category='Variable')
