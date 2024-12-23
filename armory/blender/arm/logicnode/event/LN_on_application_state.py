from arm.logicnode.arm_nodes import *

class OnApplicationStateNode(ArmLogicTreeNode):
    """Listens to different application state changes."""
    bl_idname = 'LNOnApplicationStateNode'
    bl_label = 'On Application State'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'On Foreground')
        self.add_output('ArmNodeSocketAction', 'On Background')
        self.add_output('ArmNodeSocketAction', 'On Shutdown')
