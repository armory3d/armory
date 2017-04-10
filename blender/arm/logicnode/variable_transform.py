import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TransformNode(Node, ArmLogicTreeNode):
    '''Transform node'''
    bl_idname = 'LNTransformNode'
    bl_label = 'Transform'
    bl_icon = 'SOUND'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Location')
        self.inputs.new('NodeSocketVector', 'Rotation')
        self.inputs.new('NodeSocketVector', 'Scale')
        self.inputs[-1].default_value = [1.0, 1.0, 1.0]
        self.outputs.new('NodeSocketShader', 'Transform')

add_node(TransformNode, category='Variable')
