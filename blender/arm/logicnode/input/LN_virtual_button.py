import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class VirtualButtonNode(Node, ArmLogicTreeNode):
    '''Virtual button node'''
    bl_idname = 'LNMergedVirtualButtonNode'
    bl_label = 'Virtual Button'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Started')
    property1: StringProperty(name='', default='button')

    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(VirtualButtonNode, category=MODULE_AS_CATEGORY, section='virtual')
