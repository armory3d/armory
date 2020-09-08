import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LookAtNode(ArmLogicTreeNode):
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
        self.add_input('NodeSocketVector', 'From Location')
        self.add_input('NodeSocketVector', 'To Location')
        self.add_output('NodeSocketVector', 'Rotation')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(LookAtNode, category=MODULE_AS_CATEGORY, section='rotation')
