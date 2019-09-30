import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetTextColorNode(Node, ArmLogicTreeNode):
    '''Set canvas text color'''
    bl_idname = 'LNCanvasSetTextColorNode'
    bl_label = 'Canvas Set Text Color'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketFloat', 'R')
        self.inputs.new('NodeSocketFloat', 'G')
        self.inputs.new('NodeSocketFloat', 'B')
        self.inputs.new('NodeSocketFloat', 'A')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetTextColorNode, category='Canvas')
