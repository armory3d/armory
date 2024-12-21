from arm.logicnode.arm_nodes import *

class ConfirmNode(ArmLogicTreeNode):
    """Open a window alert with the give string value and returns true or false 
    according to the user answer (works only for web browsers)."""
    bl_idname = 'LNConfirmNode'
    bl_label = 'Confirm'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'String')

        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
