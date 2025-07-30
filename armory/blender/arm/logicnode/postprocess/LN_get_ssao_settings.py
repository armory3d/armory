from arm.logicnode.arm_nodes import *

class SSAOGetNode(ArmLogicTreeNode):
    """Returns the SSAO post-processing settings."""
    bl_idname = 'LNSSAOGetNode'
    bl_label = 'Get SSAO Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Radius')
        self.add_output('ArmFloatSocket', 'Strength')
        self.add_output('ArmFloatSocket', 'Max Steps')
