import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class NoneNode(Node, ArmLogicTreeNode):
    '''None node'''
    bl_idname = 'LNNoneNode'
    bl_label = 'None'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.outputs.new('NodeSocketShader', 'None')

add_node(NoneNode, category='Value')
