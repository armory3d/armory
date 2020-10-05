from arm.logicnode.arm_nodes import *

class ResumeActionNode(ArmLogicTreeNode):
    """Resumes the given action."""
    bl_idname = 'LNResumeActionNode'
    bl_label = 'Resume Action'
    arm_version = 1

    def init(self, context):
        super(ResumeActionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ResumeActionNode, category=PKG_AS_CATEGORY)
