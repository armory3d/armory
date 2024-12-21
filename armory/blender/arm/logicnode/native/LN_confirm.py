from arm.logicnode.arm_nodes import *

class ConfirmNode(ArmLogicTreeNode):
    """Open a window alert with the give string value and returns true or false 
    according to the user answer (works only for web browsers).

    @input String: message to display.

    @output True: return in case user select yes/ok.
    @output False: return in case user select no/cancel.
    """
    bl_idname = 'LNConfirmNode'
    bl_label = 'Confirm'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'String')

        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
