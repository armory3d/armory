import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetChildrenNode(Node, ArmLogicTreeNode):
    '''Get children node'''
    bl_idname = 'LNGetChildrenNode'
    bl_label = 'Get Children'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketArray', 'Array')

add_node(GetChildrenNode, category='Value')
