from arm.logicnode.arm_nodes import *

class PauseActionNode(ArmLogicTreeNode):
    """Pauses the given action."""
    bl_idname = 'LNPauseActionNode'
    bl_label = 'Pause Action'
    bl_description = "Please use the \"Set Action Paused\" node instead"
    bl_icon = 'ERROR'
    arm_is_obsolete = True
    arm_version = 2

    def init(self, context):
        super(PauseActionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')
