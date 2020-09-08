import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ContainsStringNode(ArmLogicTreeNode):
    """Contains string node"""
    bl_idname = 'LNContainsStringNode'
    bl_label = 'Contains String'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Contains', 'Contains', 'Contains'),
                 ('Starts With', 'Starts With', 'Starts With'),
                 ('Ends With', 'Ends With', 'Ends With'),
                 ],
        name='', default='Contains')

    def init(self, context):
        self.add_input('NodeSocketString', 'String')
        self.add_input('NodeSocketString', 'Find')
        self.add_output('NodeSocketBool', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(ContainsStringNode, category=MODULE_AS_CATEGORY)
