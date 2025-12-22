from arm.logicnode.arm_nodes import *

class SetTilesheetNode(ArmLogicTreeNode):
    """Set the tilesheet by material reference."""
    bl_idname = 'LNSetTilesheetNode'
    bl_label = 'Set Tilesheet'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Material')
        self.add_input('ArmStringSocket', 'Action')

        self.add_output('ArmNodeSocketAction', 'Out')