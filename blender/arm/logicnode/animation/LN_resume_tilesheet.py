import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ResumeTilesheetNode(ArmLogicTreeNode):
    '''Resume tilesheet node'''
    bl_idname = 'LNResumeTilesheetNode'
    bl_label = 'Resume Tilesheet'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ResumeTilesheetNode, category=MODULE_AS_CATEGORY)
