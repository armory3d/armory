import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnInputNode(Node, ArmLogicTreeNode):
    '''On input node'''
    bl_idname = 'LNOnInputNode'
    bl_label = 'On Input'
    bl_icon = 'CURVE_PATH'
    property0 = EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Down')
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketOperator', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnInputNode, category='Event')
