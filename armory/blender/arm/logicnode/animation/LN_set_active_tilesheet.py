from arm.logicnode.arm_nodes import *

class SetActiveTilesheetNode(ArmLogicTreeNode):
    """Set the active tilesheet."""
    bl_idname = 'LNSetActiveTilesheetNode'
    bl_label = 'Set Active Tilesheet'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Tilesheet')
        self.add_input('ArmStringSocket', 'Action')

        self.add_output('ArmNodeSocketAction', 'Out')