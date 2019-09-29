import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SplitStringNode(Node, ArmLogicTreeNode):
    '''Split string node'''
    bl_idname = 'LNSplitStringNode'
    bl_label = 'Split String'
    bl_icon = 'CURVE_PATH'

    def init(self, context):
        self.outputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketString', 'String')
        self.inputs.new('NodeSocketString', 'Split')

add_node(SplitStringNode, category='Value')