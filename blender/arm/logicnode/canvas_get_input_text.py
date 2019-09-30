import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetInputTextNode(Node, ArmLogicTreeNode):
    '''Get canvas input text'''
    bl_idname = 'LNCanvasGetInputTextNode'
    bl_label = 'Canvas Get Input Text'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('NodeSocketString', 'Value')

add_node(CanvasGetInputTextNode, category='Canvas')
