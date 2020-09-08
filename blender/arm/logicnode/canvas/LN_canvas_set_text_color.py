import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetTextColorNode(ArmLogicTreeNode):
    '''Set canvas text color'''
    bl_idname = 'LNCanvasSetTextColorNode'
    bl_label = 'Canvas Set Text Color'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'R')
        self.add_input('NodeSocketFloat', 'G')
        self.add_input('NodeSocketFloat', 'B')
        self.add_input('NodeSocketFloat', 'A')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetTextColorNode, category=MODULE_AS_CATEGORY)
