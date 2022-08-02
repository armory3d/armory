from arm.logicnode.arm_nodes import *

class SSAOSetNode(ArmLogicTreeNode):
    """Set the SSAO post-processing settings."""
    bl_idname = 'LNSSAOSetNode'
    bl_label = 'Set SSAO Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Radius', default_value=1.0)
        self.add_input('ArmFloatSocket', 'Strength', default_value=5.0)
        self.add_input('ArmIntSocket', 'Max Steps', default_value=8)

        self.add_output('ArmNodeSocketAction', 'Out')
