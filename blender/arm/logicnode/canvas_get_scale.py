import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetScaleNode(Node, ArmLogicTreeNode):
    '''Get canvas element scale'''
    bl_idname = 'LNCanvasGetScaleNode'
    bl_label = 'Canvas Get Scale'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketInt', 'Height')
        self.outputs.new('NodeSocketInt', 'Width')

add_node(CanvasGetScaleNode, category='Canvas')
