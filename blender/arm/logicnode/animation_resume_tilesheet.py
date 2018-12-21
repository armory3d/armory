import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ResumeTilesheetNode(Node, ArmLogicTreeNode):
    '''Resume tilesheet node'''
    bl_idname = 'LNResumeTilesheetNode'
    bl_label = 'Resume Tilesheet'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ResumeTilesheetNode, category='Animation')
