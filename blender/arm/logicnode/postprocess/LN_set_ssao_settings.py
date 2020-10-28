from arm.logicnode.arm_nodes import *

class SSAOSetNode(ArmLogicTreeNode):
    """Set the SSAO post-processing settings."""
    bl_idname = 'LNSSAOSetNode'
    bl_label = 'Set SSAO Settings'
    arm_version = 1

    def init(self, context):
        super(SSAOSetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Radius', default_value=1.0)
        self.add_input('NodeSocketFloat', 'Strength', default_value=5.0)
        self.add_input('NodeSocketInt', 'Max Steps', default_value=8)
        self.add_output('ArmNodeSocketAction', 'Out')
