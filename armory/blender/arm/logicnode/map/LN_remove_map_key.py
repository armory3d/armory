from arm.logicnode.arm_nodes import *


class RemoveMapKeyNode(ArmLogicTreeNode):
    """Remove Map Key"""
    bl_idname = 'LNRemoveMapKeyNode'
    bl_label = 'Remove Map Key'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Map')
        self.add_input('ArmDynamicSocket', 'Key')

        self.add_output('ArmNodeSocketAction', 'Out')
