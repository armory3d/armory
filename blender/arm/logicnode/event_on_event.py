import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnEventNode(Node, ArmLogicTreeNode):
    '''On event node'''
    bl_idname = 'LNOnEventNode'
    bl_label = 'On Event'
    bl_icon = 'CURVE_PATH'
    property0: StringProperty(name='', default='')
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnEventNode, category='Event')
