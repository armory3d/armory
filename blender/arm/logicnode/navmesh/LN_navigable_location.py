import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class NavigableLocationNode(ArmLogicTreeNode):
    """Navigable location node"""
    bl_idname = 'LNNavigableLocationNode'
    bl_label = 'Navigable Location'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketShader', 'Location')

add_node(NavigableLocationNode, category=MODULE_AS_CATEGORY)
