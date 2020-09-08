import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PauseTilesheetNode(Node, ArmLogicTreeNode):
    '''Pause tilesheet node'''
    bl_idname = 'LNPauseTilesheetNode'
    bl_label = 'Pause Tilesheet'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(PauseTilesheetNode, category=MODULE_AS_CATEGORY, section='tilesheet')
