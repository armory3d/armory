from arm.logicnode.arm_nodes import *

class SSRGetNode(ArmLogicTreeNode):
    """Returns the SSR post-processing settings."""
    bl_idname = 'LNSSRGetNode'
    bl_label = 'Get SSR Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'SSR Step')
        self.add_output('ArmFloatSocket', 'SSR Step Min')
        self.add_output('ArmFloatSocket', 'SSR Search')
        self.add_output('ArmFloatSocket', 'SSR Falloff')
        self.add_output('ArmFloatSocket', 'SSR Jitter')
