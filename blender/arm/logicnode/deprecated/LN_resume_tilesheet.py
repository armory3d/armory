from arm.logicnode.arm_nodes import *

class ResumeTilesheetNode(ArmLogicTreeNode):
    """Resumes the given tilesheet action."""
    bl_idname = 'LNResumeTilesheetNode'
    bl_label = 'Resume Tilesheet'
    bl_description = "Please use the \"Set Tilesheet Enabled\" node instead"
    bl_icon='ERROR'
    arm_version = 2

    def init(self, context):
        super(ResumeTilesheetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ResumeTilesheetNode, category=PKG_AS_CATEGORY, is_obsolete=True)
