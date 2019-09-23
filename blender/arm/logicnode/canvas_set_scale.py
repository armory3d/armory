import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetScaleNode(Node, ArmLogicTreeNode):
    '''Set canvas element scale'''
    bl_idname = 'LNCanvasSetScaleNode'
    bl_label = 'Canvas Set Scale'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketInt', 'Height')
        self.inputs.new('NodeSocketInt', 'Width')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetScaleNode, category='Canvas')
