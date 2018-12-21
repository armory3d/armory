import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ScreenToWorldSpaceNode(Node, ArmLogicTreeNode):
    '''Screen to world space node'''
    bl_idname = 'LNScreenToWorldSpaceNode'
    bl_label = 'Screen To World Space'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('NodeSocketVector', 'Vector')

add_node(ScreenToWorldSpaceNode, category='Value')
