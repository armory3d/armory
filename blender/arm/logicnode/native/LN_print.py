from arm.logicnode.arm_nodes import *

class PrintNode(ArmLogicTreeNode):
    """Print the given value to the console."""
    bl_idname = 'LNPrintNode'
    bl_label = 'Print'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'String')

        self.add_output('ArmNodeSocketAction', 'Out')
