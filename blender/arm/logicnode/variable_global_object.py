import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GlobalObjectNode(Node, ArmLogicTreeNode):
    '''Global object node'''
    bl_idname = 'LNGlobalObjectNode'
    bl_label = 'Global Object'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(GlobalObjectNode, category='Variable')
