import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetActivationStateNode(ArmLogicTreeNode):
    """Use to set the activation state of a rigid body."""
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
        self.inputs.new('ArmNodeSocketObject', 'Rigid Body')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(SetActivationStateNode, category=PKG_AS_CATEGORY)
