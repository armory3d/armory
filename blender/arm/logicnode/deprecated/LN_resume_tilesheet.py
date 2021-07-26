from arm.logicnode.arm_nodes import *


@deprecated('Set Tilesheet Paused')
class ResumeTilesheetNode(ArmLogicTreeNode):
    """Resumes the given tilesheet action."""
    bl_idname = 'LNResumeTilesheetNode'
    bl_label = 'Resume Tilesheet'
    bl_description = "Please use the \"Set Tilesheet Paused\" node instead"
    arm_category = 'Animation'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')
