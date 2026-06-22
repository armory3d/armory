from arm.logicnode.arm_nodes import *

class ShutdownNode(ArmLogicTreeNode):
    """Closes the application."""
    bl_idname = 'LNShutdownNode'
    bl_label = 'Shutdown'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
