from arm.logicnode.arm_nodes import *


@deprecated('Set Action Paused')
class PauseActionNode(ArmLogicTreeNode):
    """Pauses the given action."""
    bl_idname = 'LNPauseActionNode'
    bl_label = 'Pause Action'
    bl_description = "Please use the \"Set Action Paused\" node instead"
    arm_category = 'Animation'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')
