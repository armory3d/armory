import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class NavigableLocationNode(Node, ArmLogicTreeNode):
    '''Navigable location node'''
    bl_idname = 'LNNavigableLocationNode'
    bl_label = 'Navigable Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Location')

add_node(NavigableLocationNode, category='Navmesh')
