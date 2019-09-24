import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetPBNode(Node, ArmLogicTreeNode):
    '''Get canvas progress bar'''
    bl_idname = 'LNCanvasGetPBNode'
    bl_label = 'Canvas Get Progress Bar'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketInt', 'At')
        self.outputs.new('NodeSocketInt', 'Max')

add_node(CanvasGetPBNode, category='Canvas')