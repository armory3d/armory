import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ParseFloatNode(Node, ArmLogicTreeNode):
    '''Parse float node'''
    bl_idname = 'LNParseFloatNode'
    bl_label = 'Parse float'
    bl_icon = 'CURVE_PATH'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Float')
        self.inputs.new('NodeSocketString', 'String')

add_node(ParseFloatNode, category='Value')