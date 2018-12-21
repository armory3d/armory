import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class VolumeTriggerNode(Node, ArmLogicTreeNode):
    '''Volume trigger node'''
    bl_idname = 'LNVolumeTriggerNode'
    bl_label = 'Volume Trigger'
    bl_icon = 'QUESTION'
    property0: EnumProperty(
        items = [('Enter', 'Enter', 'Enter'),
                 ('Leave', 'Leave', 'Leave'),
                 ('Overlap', 'Overlap', 'Overlap')],
        name='', default='Enter')
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmNodeSocketObject', 'Volume')
        self.inputs[-1].default_value = 'Volume'
        self.outputs.new('NodeSocketBool', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(VolumeTriggerNode, category='Value')
