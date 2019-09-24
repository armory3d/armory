import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetRotationNode(Node, ArmLogicTreeNode):
    '''Get canvas element rotation'''
    bl_idname = 'LNCanvasGetRotationNode'
    bl_label = 'Canvas Get Rotation'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketFloat', 'Rad')

add_node(CanvasGetRotationNode, category='Canvas')
