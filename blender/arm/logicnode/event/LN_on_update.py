import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnUpdateNode(ArmLogicTreeNode):
    '''On update node'''
    bl_idname = 'LNOnUpdateNode'
    bl_label = 'On Update'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Update', 'Update', 'Update'),
                 ('Late Update', 'Late Update', 'Late Update'),
                 ('Physics Pre-Update', 'Physics Pre-Update', 'Physics Pre-Update')],
        name='On', default='Update')

    def init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(OnUpdateNode, category=MODULE_AS_CATEGORY)
