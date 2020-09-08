import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnContactArrayNode(ArmLogicTreeNode):
    '''On contact array node'''
    bl_idname = 'LNOnContactArrayNode'
    bl_label = 'On Contact Array'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Begin', 'Begin', 'Begin'),
                 ('End', 'End', 'End'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Begin')

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object 1')
        self.add_input('ArmNodeSocketArray', 'Objects')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnContactArrayNode, category=MODULE_AS_CATEGORY, section='contact')
