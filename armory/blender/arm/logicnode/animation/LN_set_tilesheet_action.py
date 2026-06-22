from arm.logicnode.arm_nodes import *

class SetTilesheetActionNode(ArmLogicTreeNode):
    """Sets the tilesheet action for the given object."""
    bl_idname = 'LNSetTilesheetActionNode'
    bl_label = 'Set Tilesheet Action'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action')

        self.add_output('ArmNodeSocketAction', 'Out')