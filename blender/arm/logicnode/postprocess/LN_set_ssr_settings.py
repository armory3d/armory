from arm.logicnode.arm_nodes import *

class SSRSetNode(ArmLogicTreeNode):
    """Use to set the SSR post-processing settings."""
    bl_idname = 'LNSSRSetNode'
    bl_label = 'Set SSR Settings'
    arm_version = 1

    def init(self, context):
        super(SSRSetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'SSR Step', default_value=0.04)
        self.add_input('NodeSocketFloat', 'SSR Step Min', default_value=0.05)
        self.add_input('NodeSocketFloat', 'SSR Search', default_value=5.0)
        self.add_input('NodeSocketFloat', 'SSR Falloff', default_value=5.0)
        self.add_input('NodeSocketFloat', 'SSR Jitter', default_value=0.6)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SSRSetNode, category=PKG_AS_CATEGORY)
