import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetActivationStateNode(ArmLogicTreeNode):
    """Sets the activation state of the given rigid body."""
    bl_idname = 'LNSetActivationStateNode'
    bl_label = 'Set RB Activation State'
    bl_icon = 'NONE'
    arm_version = 1
    property0: EnumProperty(
        items = [('Inactive', 'Inactive', 'Inactive'),
                 ('Active', 'Active', 'Active'),
                 ('Always Active', 'Always Active', 'Always Active'),
                 ('Always Inactive', 'Always Inactive', 'Always Inactive'),
                 ],
        name='', default='Inactive')

    def init(self, context):
        super(SetActivationStateNode, self).init(context)
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'RB')

        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
