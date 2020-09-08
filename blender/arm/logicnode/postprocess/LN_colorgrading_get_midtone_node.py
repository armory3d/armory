import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorgradingGetMidtoneNode(Node, ArmLogicTreeNode):
    '''Colorgrading Get Midtone node'''
    bl_idname = 'LNColorgradingGetMidtoneNode'
    bl_label = 'Colorgrading Get Midtone'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketVector', 'Saturation')
        self.outputs.new('NodeSocketVector', 'Contrast')
        self.outputs.new('NodeSocketVector', 'Gamma')
        self.outputs.new('NodeSocketVector', 'Gain')
        self.outputs.new('NodeSocketVector', 'Offset')

add_node(ColorgradingGetMidtoneNode, category=MODULE_AS_CATEGORY, section='colorgrading')
