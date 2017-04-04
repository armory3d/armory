import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class InputNode(Node, ArmLogicTreeNode):
    '''Input node'''
    bl_idname = 'LNInputNode'
    bl_label = 'Input'
    bl_icon = 'CURVE_PATH'
    property0 = EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Down')
    
    def init(self, context):
        self.outputs.new('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(InputNode, category='Value')
