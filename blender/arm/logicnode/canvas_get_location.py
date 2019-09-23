import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetLocationNode(Node, ArmLogicTreeNode):
    '''Get canvas element location'''
    bl_idname = 'LNCanvasGetLocationNode'
    bl_label = 'Canvas Get Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketFloat', 'X')
        self.outputs.new('NodeSocketFloat', 'Y')

add_node(CanvasGetLocationNode, category='Canvas')
