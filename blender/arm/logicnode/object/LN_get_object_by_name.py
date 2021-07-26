import bpy

from arm.logicnode.arm_nodes import *


class GetObjectNode(ArmLogicTreeNode):
    """Searches for a object that uses the given name in the current active scene and returns it."""

    bl_idname = 'LNGetObjectNode'
    bl_label = 'Get Object by Name'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Name')

        self.add_output('ArmNodeSocketObject', 'Object')
