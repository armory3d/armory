import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetParentNode(Node, ArmLogicTreeNode):
    '''Get parent node'''
    bl_idname = 'LNGetParentNode'
    bl_label = 'Get Parent'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(GetParentNode, category='Value')
