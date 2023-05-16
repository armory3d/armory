from arm.logicnode.arm_nodes import *


class MapKeyExistsNode(ArmLogicTreeNode):
    """Map Key Exists"""
    bl_idname = 'LNMapKeyExistsNode'
    bl_label = 'Map Key Exists'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Map')
        self.add_input('ArmDynamicSocket', 'Key')

        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')