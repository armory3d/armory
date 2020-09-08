import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetLocationNode(ArmLogicTreeNode):
    """Set canvas element location"""
    bl_idname = 'LNCanvasSetLocationNode'
    bl_label = 'Canvas Set Location'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'X')
        self.add_input('NodeSocketFloat', 'Y')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetLocationNode, category=MODULE_AS_CATEGORY)
