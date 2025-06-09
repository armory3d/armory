from arm.logicnode.arm_nodes import *

class SetWorldNode(ArmLogicTreeNode):
    """Gets the World of the active scene."""
    bl_idname = 'LNGetWorldNode'
    bl_label = 'Get World'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmStringSocket', 'World')