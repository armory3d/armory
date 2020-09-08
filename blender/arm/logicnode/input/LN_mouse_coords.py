import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MouseCoordsNode(ArmLogicTreeNode):
    """Mouse coords node"""
    bl_idname = 'LNMouseCoordsNode'
    bl_label = 'Mouse Coords'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketVector', 'Coords')
        self.add_output('NodeSocketVector', 'Movement')
        self.add_output('NodeSocketInt', 'Wheel')

add_node(MouseCoordsNode, category=MODULE_AS_CATEGORY, section='mouse')
