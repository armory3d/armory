import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetSliderNode(Node, ArmLogicTreeNode):
    '''Set canvas text'''
    bl_idname = 'LNCanvasSetSliderNode'
    bl_label = 'Canvas Set Slider'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketFloat', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetSliderNode, category='Canvas')
