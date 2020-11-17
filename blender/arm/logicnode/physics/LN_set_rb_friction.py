import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetFrictionNode (ArmLogicTreeNode):
    """Sets the friction of the given rigid body."""
    bl_idname = 'LNSetFrictionNode'
    bl_label = 'Set RB Friction'
    bl_icon = 'NONE'
    arm_version = 1

    def init(self, context):
        super(SetFrictionNode, self).init(context)
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'RB')
        self.inputs.new('NodeSocketFloat', 'Friction')

        self.outputs.new('ArmNodeSocketAction', 'Out')
