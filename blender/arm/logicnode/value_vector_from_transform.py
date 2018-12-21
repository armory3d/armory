import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class VectorFromTransformNode(Node, ArmLogicTreeNode):
    '''Vector from transform node'''
    bl_idname = 'LNVectorFromTransformNode'
    bl_label = 'Vector From Transform'
    bl_icon = 'QUESTION'
    property0: EnumProperty(
        items = [('Up', 'Up', 'Up'),
                 ('Right', 'Right', 'Right'),
                 ('Look', 'Look', 'Look'),
                 ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='Look')

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Transform')
        self.outputs.new('NodeSocketVector', 'Vector')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(VectorFromTransformNode, category='Value')
