import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ColorgradingGetHighlightNode(Node, ArmLogicTreeNode):
    '''Colorgrading Get Highlight node'''
    bl_idname = 'LNColorgradingGetHighlightNode'
    bl_label = 'Colorgrading Get Highlight'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'HightlightMin')
        self.outputs.new('NodeSocketVector', 'Saturation')
        self.outputs.new('NodeSocketVector', 'Contrast')
        self.outputs.new('NodeSocketVector', 'Gamma')
        self.outputs.new('NodeSocketVector', 'Gain')
        self.outputs.new('NodeSocketVector', 'Offset')

add_node(ColorgradingGetHighlightNode, category='Postprocess')