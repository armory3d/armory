import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMouseVisibleNode(Node, ArmLogicTreeNode):
    '''Get Mouse Visible node'''
    bl_idname = 'LNGetMouseVisibleNode'
    bl_label = 'Get Mouse Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketBool', 'Visible')

add_node(GetMouseVisibleNode, category='Value')
