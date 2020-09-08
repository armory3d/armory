import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorgradingGetShadowNode(ArmLogicTreeNode):
    """Colorgrading Get Shadow node"""
    bl_idname = 'LNColorgradingGetShadowNode'
    bl_label = 'Colorgrading Get Shadow'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'ShadowMax')
        self.add_output('NodeSocketVector', 'Saturation')
        self.add_output('NodeSocketVector', 'Contrast')
        self.add_output('NodeSocketVector', 'Gamma')
        self.add_output('NodeSocketVector', 'Gain')
        self.add_output('NodeSocketVector', 'Offset')

add_node(ColorgradingGetShadowNode, category=MODULE_AS_CATEGORY, section='colorgrading')
