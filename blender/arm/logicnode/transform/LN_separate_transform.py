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
        self.inputs.new('NodeSocketShader', 'Transform')
        self.outputs.new('NodeSocketVector', 'Location')
        self.outputs.new('NodeSocketVector', 'Rotation')
        self.outputs.new('NodeSocketVector', 'Scale')

add_node(SeparateTransformNode, category=MODULE_AS_CATEGORY)
