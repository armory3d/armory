import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WindowInfoNode(ArmLogicTreeNode):
    """Window info node"""
    bl_idname = 'LNWindowInfoNode'
    bl_label = 'Window Info'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')

add_node(WindowInfoNode, category=MODULE_AS_CATEGORY, section='screen')
