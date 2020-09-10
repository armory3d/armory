import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetShadowVisibleNode(Node, ArmLogicTreeNode):
    '''Get Shadow Visible node'''
    bl_idname = 'LNGetShadowVisibleNode'
    bl_label = 'Get Shadow Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Visible')

add_node(GetShadowVisibleNode, category='Value')
