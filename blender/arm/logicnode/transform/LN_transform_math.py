import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TransformMathNode(ArmLogicTreeNode):
    '''Transform math node'''
    bl_idname = 'LNTransformMathNode'
    bl_label = 'Transform Math'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketShader', 'Transform')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('NodeSocketShader', 'Transform')

add_node(TransformMathNode, category=MODULE_AS_CATEGORY)
