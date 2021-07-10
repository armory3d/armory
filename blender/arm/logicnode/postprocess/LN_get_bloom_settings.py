from arm.logicnode.arm_nodes import *

class BloomGetNode(ArmLogicTreeNode):
    """Returns the bloom post-processing settings."""
    bl_idname = 'LNBloomGetNode'
    bl_label = 'Get Bloom Settings'
    arm_version = 1

    def init(self, context):
        super(BloomGetNode, self).init(context)
        self.add_output('ArmFloatSocket', 'Threshold')
        self.add_output('ArmFloatSocket', 'Strength')
        self.add_output('ArmFloatSocket', 'Radius')
