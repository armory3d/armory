import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class VectorClampToSizeNode(Node, ArmLogicTreeNode):
    '''Vector clamp to size node'''
    bl_idname = 'LNVectorClampToSizeNode'
    bl_label = 'Vector Clamp To Size'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Vector')
        self.inputs[-1].default_value = [0.5, 0.5, 0.5]
        self.inputs.new('NodeSocketFloat', 'Min')
        self.inputs.new('NodeSocketFloat', 'Max')
        self.outputs.new('NodeSocketVector', 'Vector')

add_node(VectorClampToSizeNode, category='Value')
