import bpy

from arm.logicnode.arm_nodes import *


class GetObjectByUidNode(ArmLogicTreeNode):
    """Searches for a object with this uid in the current active scene and returns it."""

    bl_idname = 'LNGetObjectByUidNode'
    bl_label = 'Get Object By Uid'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Uid')

        self.add_output('ArmNodeSocketObject', 'Object')
