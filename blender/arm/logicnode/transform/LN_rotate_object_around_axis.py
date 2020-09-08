import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RotateObjectAroundAxisNode(ArmLogicTreeNode):
    '''Rotate object around axis node'''
    bl_idname = 'LNRotateObjectAroundAxisNode'
    bl_label = 'Rotate Object Around Axis'
    bl_description = 'Rotate Object Around Axis (Depreciated: use "Rotate Object")'
    bl_icon = 'ERROR'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Axis')
        self.inputs[-1].default_value = [0, 0, 1]
        self.inputs.new('NodeSocketFloat', 'Angle')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.label(text='Depreciated. Consider using "Rotate Object"')

add_node(RotateObjectAroundAxisNode, category=MODULE_AS_CATEGORY, section='rotation')
