import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WorldToScreenSpaceNode(Node, ArmLogicTreeNode):
    '''World to screen space node'''
    bl_idname = 'LNWorldToScreenSpaceNode'
    bl_label = 'World To Screen Space'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('NodeSocketVector', 'Vector')

add_node(WorldToScreenSpaceNode, category='Value')
