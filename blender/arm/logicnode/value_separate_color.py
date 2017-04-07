import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SeparateColorNode(Node, ArmLogicTreeNode):
    '''Separate color node'''
    bl_idname = 'LNSeparateColorNode'
    bl_label = 'Separate RGB'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketColor', 'Color')
        self.inputs[-1].default_value = [0.8, 0.8, 0.8, 1]
        self.outputs.new('NodeSocketFloat', 'R')
        self.outputs.new('NodeSocketFloat', 'G')
        self.outputs.new('NodeSocketFloat', 'B')

add_node(SeparateColorNode, category='Value')
