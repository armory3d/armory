from arm.logicnode.arm_nodes import *

class ResumeTilesheetNode(ArmLogicTreeNode):
    """Use to resume a tilesheet."""
    bl_idname = 'LNResumeTilesheetNode'
    bl_label = 'Resume Tilesheet'
    arm_version = 1

    def init(self, context):
        super(ResumeTilesheetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ResumeTilesheetNode, category=PKG_AS_CATEGORY)
