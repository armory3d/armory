import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class FloatNode(ArmLogicTreeNode):
    '''Float node'''
    bl_idname = 'LNFloatNode'
    bl_label = 'Float'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Value')
        self.outputs.new('NodeSocketFloat', 'Float')

add_node(FloatNode, category=MODULE_AS_CATEGORY)
