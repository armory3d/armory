from arm.logicnode.arm_nodes import *

class SyncActionsNode(ArmLogicTreeNode):
    """Sync two actions when blending from one to the other such that Frame A and B in both actions align."""

    bl_idname = 'LNSyncActionNode'
    bl_label = 'Sync Action'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'From ID')
        self.add_input('ArmIntSocket', 'Frame A', default_value=0)
        self.add_input('ArmIntSocket', 'Frame B', default_value=-1)
        self.add_input('ArmBoolSocket', 'Reset Speed', default_value=True)
        self.add_input('ArmStringSocket', 'To ID')
        self.add_input('ArmIntSocket', 'Frame A', default_value=0)
        self.add_input('ArmIntSocket', 'Frame B', default_value=-1)

        self.add_output('ArmNodeSocketAction', 'Out')
