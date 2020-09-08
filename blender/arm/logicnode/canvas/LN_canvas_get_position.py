import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetPositionNode(ArmLogicTreeNode):
    """Get canvas radio and combo value"""
    bl_idname = 'LNCanvasGetPositionNode'
    bl_label = 'Canvas Get Position'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketInt', 'Value')

add_node(CanvasGetPositionNode, category=MODULE_AS_CATEGORY)
