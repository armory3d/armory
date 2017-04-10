import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class VectorNode(Node, ArmLogicTreeNode):
    '''Vector node'''
    bl_idname = 'LNVectorNode'
    bl_label = 'Vector'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'X')
        self.inputs.new('NodeSocketFloat', 'Y')
        self.inputs.new('NodeSocketFloat', 'Z')
        
        self.outputs.new('NodeSocketVector', 'Vector')

add_node(VectorNode, category='Variable')
