import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetCheckboxNode(Node, ArmLogicTreeNode):
    '''Get canvas checkbox value'''
    bl_idname = 'LNCanvasGetCheckboxNode'
    bl_label = 'Canvas Get Checkbox'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketString', 'Element')
        self.outputs.new('NodeSocketBool', 'Value')

add_node(CanvasGetCheckboxNode, category='Canvas')
