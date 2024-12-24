from arm.logicnode.arm_nodes import *


class GetMapValueNode(ArmLogicTreeNode):
    """Get Map Value"""
    bl_idname = 'LNGetMapValueNode'
    bl_label = 'Get Map Value'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmDynamicSocket', 'Map')
        self.add_input('ArmDynamicSocket', 'Key')

        self.add_output('ArmDynamicSocket', 'Value')
