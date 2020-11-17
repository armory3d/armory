from arm.logicnode.arm_nodes import *

class BloomSetNode(ArmLogicTreeNode):
    """Set the bloom post-processing settings."""
    bl_idname = 'LNBloomSetNode'
    bl_label = 'Set Bloom Settings'
    arm_version = 1

    def init(self, context):
        super(BloomSetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Threshold', default_value=1.00)
        self.add_input('NodeSocketFloat', 'Strength', default_value=3.50)
        self.add_input('NodeSocketFloat', 'Radius', default_value=3.0)

        self.add_output('ArmNodeSocketAction', 'Out')
