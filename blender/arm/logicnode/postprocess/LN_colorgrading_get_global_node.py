import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorgradingGetGlobalNode(Node, ArmLogicTreeNode):
    '''Colorgrading Get Global node'''
    bl_idname = 'LNColorgradingGetGlobalNode'
    bl_label = 'Colorgrading Get Global'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Whitebalance')
        self.outputs.new('NodeSocketVector', 'Tint')
        self.outputs.new('NodeSocketVector', 'Saturation')
        self.outputs.new('NodeSocketVector', 'Contrast')
        self.outputs.new('NodeSocketVector', 'Gamma')
        self.outputs.new('NodeSocketVector', 'Gain')
        self.outputs.new('NodeSocketVector', 'Offset')

add_node(ColorgradingGetGlobalNode, category=MODULE_AS_CATEGORY, section='colorgrading')
