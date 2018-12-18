import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetTextNode(Node, ArmLogicTreeNode):
    '''Set canvas text'''
    bl_idname = 'LNCanvasSetTextNode'
    bl_label = 'Canvas Set Text'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketString', 'Text')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetTextNode, category='Canvas')
