import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnContactArrayNode(Node, ArmLogicTreeNode):
    '''On contact array node'''
    bl_idname = 'LNOnContactArrayNode'
    bl_label = 'On Contact (Array)'
    bl_icon = 'QUESTION'
    property0: EnumProperty(
        items = [('Begin', 'Begin', 'Begin'),
                 ('End', 'End', 'End'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Begin')

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object 1')
        self.inputs.new('ArmNodeSocketArray', 'Objects')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnContactArrayNode, category='Physics')
