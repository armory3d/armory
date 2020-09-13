from arm.logicnode.arm_nodes import *

class SSAOSetNode(ArmLogicTreeNode):
    """Set SSAO Effect"""
    bl_idname = 'LNSSAOSetNode'
    bl_label = 'Set SSAO'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Radius', default_value=1.0)
        self.add_input('NodeSocketFloat', 'Strength', default_value=5.0)
        self.add_input('NodeSocketInt', 'Max Steps', default_value=8)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SSAOSetNode, category=PKG_AS_CATEGORY)
