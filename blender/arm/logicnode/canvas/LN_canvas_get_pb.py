import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetPBNode(ArmLogicTreeNode):
    """Get canvas progress bar"""
    bl_idname = 'LNCanvasGetPBNode'
    bl_label = 'Canvas Get Progress Bar'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketInt', 'At')
        self.add_output('NodeSocketInt', 'Max')

add_node(CanvasGetPBNode, category=MODULE_AS_CATEGORY)
