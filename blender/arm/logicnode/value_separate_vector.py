import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SeparateVectorNode(Node, ArmLogicTreeNode):
    '''Separate vector node'''
    bl_idname = 'LNSeparateVectorNode'
    bl_label = 'Separate XYZ'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('NodeSocketFloat', 'X')
        self.outputs.new('NodeSocketFloat', 'Y')
        self.outputs.new('NodeSocketFloat', 'Z')

add_node(SeparateVectorNode, category='Value')
