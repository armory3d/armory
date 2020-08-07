import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LookAtNode(Node, ArmLogicTreeNode):
    '''Look at node'''
    bl_idname = 'LNLookAtNode'
    bl_label = 'Look At'
    bl_icon = 'NONE'

    property0: EnumProperty(
        items = [('X', ' X', 'X'),
                 ('-X', '-X', '-X'),
                 ('Y', ' Y', 'Y'),
                 ('-Y', '-Y', '-Y'),
                 ('Z', ' Z', 'Z'),
                 ('-Z', '-Z', '-Z')],
        name='With', default='Z')

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'From Location')
        self.inputs.new('NodeSocketVector', 'To Location')
        self.outputs.new('NodeSocketVector', 'Rotation')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(LookAtNode, category='Value')
