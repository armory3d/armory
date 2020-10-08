from arm.logicnode.arm_nodes import *

class SSAOGetNode(ArmLogicTreeNode):
    """Returns the SSAO post-processing settings."""
    bl_idname = 'LNSSAOGetNode'
    bl_label = 'Get SSAO Settings'
    arm_version = 1

    def init(self, context):
        super(SSAOGetNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Radius')
        self.add_output('NodeSocketFloat', 'Strength')
        self.add_output('NodeSocketFloat', 'Max Steps')

add_node(SSAOGetNode, category=PKG_AS_CATEGORY)
