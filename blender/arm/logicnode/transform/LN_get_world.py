import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetWorldNode(Node, ArmLogicTreeNode):
    '''Get world node'''
    bl_idname = 'LNGetWorldNode'
    bl_label = 'Get World'
    bl_icon = 'NONE'

    property0: EnumProperty(
        items = [('right', 'right', 'right'),
                 ('look', 'look', 'look'),
                 ('up', 'up', 'up')],
        name='', default='right')

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Vector')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(GetWorldNode, category=MODULE_AS_CATEGORY, section='rotation')
