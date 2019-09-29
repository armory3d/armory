import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SubStrNode(Node, ArmLogicTreeNode):
    '''Sub str node'''
    bl_idname = 'LNSubStrNode'
    bl_label = 'Sub Str'
    bl_icon = 'CURVE_PATH'

    def init(self, context):
        self.outputs.new('NodeSocketString', 'String')
        self.inputs.new('NodeSocketString', 'String')
        self.inputs.new('NodeSocketInt', 'Position')
        self.inputs.new('NodeSocketInt', 'Length')

add_node(SubStrNode, category='Value')