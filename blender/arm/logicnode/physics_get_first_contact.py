import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetFirstContactNode(Node, ArmLogicTreeNode):
    '''Get first contact node'''
    bl_idname = 'LNGetFirstContactNode'
    bl_label = 'Get First Contact'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "Object")
        self.outputs.new('NodeSocketShader', "Object")

add_node(GetFirstContactNode, category='Physics')
