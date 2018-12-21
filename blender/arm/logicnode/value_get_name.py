import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetNameNode(Node, ArmLogicTreeNode):
    '''Get name node'''
    bl_idname = 'LNGetNameNode'
    bl_label = 'Get Name'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketString', 'Name')

add_node(GetNameNode, category='Value')
