from arm.logicnode.arm_nodes import *

class PrintNode(ArmLogicTreeNode):
    """Clears the system console."""
    bl_idname = 'LNClearConsoleNode'
    bl_label = 'Clear Console'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
