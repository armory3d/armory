import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetVisibleNode(Node, ArmLogicTreeNode):
    """Set Visible node"""
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Visible'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Object', 'Object', 'Object'),
                 ('Mesh', 'Mesh', 'Mesh'),
                 ('Shadow', 'Shadow', 'Shadow'),
                 ],
        name='', default='Object')

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Visible')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(SetVisibleNode, category='Action')
