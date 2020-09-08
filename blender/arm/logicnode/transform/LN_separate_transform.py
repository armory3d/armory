import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SeparateTransformNode(ArmLogicTreeNode):
    '''Separate transform node'''
    bl_idname = 'LNSeparateTransformNode'
    bl_label = 'Separate Transform'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('NodeSocketVector', 'Location')
        self.add_output('NodeSocketVector', 'Rotation')
        self.add_output('NodeSocketVector', 'Scale')

add_node(SeparateTransformNode, category=MODULE_AS_CATEGORY)
