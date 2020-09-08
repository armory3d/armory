import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorgradingGetShadowNode(Node, ArmLogicTreeNode):
    '''Colorgrading Get Shadow node'''
    bl_idname = 'LNColorgradingGetShadowNode'
    bl_label = 'Colorgrading Get Shadow'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'ShadowMax')
        self.outputs.new('NodeSocketVector', 'Saturation')
        self.outputs.new('NodeSocketVector', 'Contrast')
        self.outputs.new('NodeSocketVector', 'Gamma')
        self.outputs.new('NodeSocketVector', 'Gain')
        self.outputs.new('NodeSocketVector', 'Offset')

add_node(ColorgradingGetShadowNode, category=MODULE_AS_CATEGORY, section='colorgrading')
