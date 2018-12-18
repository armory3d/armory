import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RandomColorNode(Node, ArmLogicTreeNode):
    '''Random color node'''
    bl_idname = 'LNRandomColorNode'
    bl_label = 'Random (Color)'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')

add_node(RandomColorNode, category='Value')
