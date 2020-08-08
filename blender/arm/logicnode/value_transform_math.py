import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TransformMathNode(Node, ArmLogicTreeNode):
    '''Transform math node'''
    bl_idname = 'LNTransformMathNode'
    bl_label = 'Transform Math'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Transform')
        self.inputs.new('NodeSocketShader', 'Transform')
        self.outputs.new('NodeSocketShader', 'Transform')

add_node(TransformMathNode, category='Value')
