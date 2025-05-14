from arm.logicnode.arm_nodes import *

class SSRSetNode(ArmLogicTreeNode):
    """Set the SSR post-processing settings."""
    bl_idname = 'LNSSRSetNode'
    bl_label = 'Set SSR Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'SSR Step', default_value=0.04)
        self.add_input('ArmFloatSocket', 'SSR Step Min', default_value=0.05)
        self.add_input('ArmFloatSocket', 'SSR Search', default_value=5.0)
        self.add_input('ArmFloatSocket', 'SSR Falloff', default_value=5.0)
        self.add_input('ArmFloatSocket', 'SSR Jitter', default_value=0.6)

        self.add_output('ArmNodeSocketAction', 'Out')
