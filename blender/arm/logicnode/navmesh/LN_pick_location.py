import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PickLocationNode(ArmLogicTreeNode):
    """Pick location node"""
    bl_idname = 'LNPickLocationNode'
    bl_label = 'Pick Location'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Navmesh')
        self.add_input('NodeSocketVector', 'Screen Coords')
        self.add_output('NodeSocketVector', 'Location')

add_node(PickLocationNode, category=MODULE_AS_CATEGORY)
