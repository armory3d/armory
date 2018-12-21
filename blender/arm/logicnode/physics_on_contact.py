import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnContactNode(Node, ArmLogicTreeNode):
    '''On contact node'''
    bl_idname = 'LNOnContactNode'
    bl_label = 'On Contact'
    bl_icon = 'QUESTION'
    property0: EnumProperty(
        items = [('Begin', 'Begin', 'Begin'),
                 ('End', 'End', 'End'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Begin')

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object 1')
        self.inputs.new('ArmNodeSocketObject', 'Object 2')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnContactNode, category='Physics')
