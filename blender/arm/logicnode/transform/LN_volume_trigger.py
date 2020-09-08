import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class VolumeTriggerNode(ArmLogicTreeNode):
    '''Volume trigger node'''
    bl_idname = 'LNVolumeTriggerNode'
    bl_label = 'Volume Trigger'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Enter', 'Enter', 'Enter'),
                 ('Leave', 'Leave', 'Leave'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Enter')

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Volume', default_value='Volume')
        self.add_output('NodeSocketBool', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(VolumeTriggerNode, category=MODULE_AS_CATEGORY, section='misc')
