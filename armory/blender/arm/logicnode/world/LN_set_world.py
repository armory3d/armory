from arm.logicnode.arm_nodes import *

class SetWorldNode(ArmLogicTreeNode):
    """Sets the World of the active scene."""
    bl_idname = 'LNSetWorldNode'
    bl_label = 'Set World'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'World')

        self.add_output('ArmNodeSocketAction', 'Out')
