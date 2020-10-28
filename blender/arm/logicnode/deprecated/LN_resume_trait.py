from arm.logicnode.arm_nodes import *

class ResumeTraitNode(ArmLogicTreeNode):
    """Resumes the given trait."""
    bl_idname = 'LNResumeTraitNode'
    bl_label = 'Resume Trait'
    bl_description = "Please use the \"Set Trait Paused\" node instead"
    bl_icon = 'ERROR'
    arm_is_obsolete = True
    arm_version = 2

    def init(self, context):
        super(ResumeTraitNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('ArmNodeSocketAction', 'Out')
