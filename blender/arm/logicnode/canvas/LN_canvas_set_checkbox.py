import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetCheckBoxNode(Node, ArmLogicTreeNode):
    '''Set canvas check box'''
    bl_idname = 'LNCanvasSetCheckBoxNode'
    bl_label = 'Canvas Set Checkbox'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketBool', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetCheckBoxNode, category=MODULE_AS_CATEGORY)
