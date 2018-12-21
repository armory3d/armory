import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SelfNode(Node, ArmLogicTreeNode):
    '''Self node'''
    bl_idname = 'LNSelfNode'
    bl_label = 'Self'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(SelfNode, category='Value')
