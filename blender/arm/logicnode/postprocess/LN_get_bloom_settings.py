from arm.logicnode.arm_nodes import *

class BloomGetNode(ArmLogicTreeNode):
    """Use to get the bloom post-processing settings."""
    bl_idname = 'LNBloomGetNode'
    bl_label = 'Get Bloom Settings'
    arm_version = 1

    def init(self, context):
        super(BloomGetNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Threshold')
        self.add_output('NodeSocketFloat', 'Strength')
        self.add_output('NodeSocketFloat', 'Radius')

add_node(BloomGetNode, category=PKG_AS_CATEGORY)
