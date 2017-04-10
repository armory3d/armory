import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorNode(Node, ArmLogicTreeNode):
    '''Color node'''
    bl_idname = 'LNColorNode'
    bl_label = 'Color'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketColor', 'Color')
        self.inputs[-1].default_value = [0.8, 0.8, 0.8, 1.0]
        self.outputs.new('NodeSocketColor', 'Color')

add_node(ColorNode, category='Variable')
