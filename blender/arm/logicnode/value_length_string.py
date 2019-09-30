import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LengthStringNode(Node, ArmLogicTreeNode):
    '''String Length node'''
    bl_idname = 'LNLengthStringNode'
    bl_label = 'String Length'
    bl_icon = 'CURVE_PATH'

    def init(self, context):
        self.outputs.new('NodeSocketInt', 'length')
        self.inputs.new('NodeSocketString', 'String')

add_node(LengthStringNode, category='Value')