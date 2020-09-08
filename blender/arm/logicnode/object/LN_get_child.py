import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetChildNode(ArmLogicTreeNode):
    """Get child node"""
    bl_idname = 'LNGetChildNode'
    bl_label = 'Get Child'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('By Name', 'By Name', 'By Name'),
                 ('Contains', 'Contains', 'Contains'),
                 ('Starts With', 'Starts With', 'Starts With'),
                 ('Ends With', 'Ends With', 'Ends With'),
                 ],
        name='', default='By Name')

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Child')
        self.add_output('ArmNodeSocketObject', 'Object')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(GetChildNode, category=MODULE_AS_CATEGORY, section='relations')
