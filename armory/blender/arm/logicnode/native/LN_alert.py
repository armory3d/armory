from arm.logicnode.arm_nodes import *

class PrintNode(ArmLogicTreeNode):
    """Open a window alert with the give string value (works only for web browsers)."""
    bl_idname = 'LNAlertNode'
    bl_label = 'Alert'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'String')

        self.add_output('ArmNodeSocketAction', 'Out')
