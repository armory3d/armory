from arm.logicnode.arm_nodes import *


class ClearMapNode(ArmLogicTreeNode):
    """Clear Map"""
    bl_idname = 'LNClearMapNode'
    bl_label = 'Clear Map'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Map')

        self.add_output('ArmNodeSocketAction', 'Out')
