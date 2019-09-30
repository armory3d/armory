import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetPositionNode(Node, ArmLogicTreeNode):
    '''Get canvas radio and combo value'''
    bl_idname = 'LNCanvasGetPositionNode'
    bl_label = 'Canvas Get Position'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('NodeSocketInt', 'Value')

add_node(CanvasGetPositionNode, category='Canvas')
