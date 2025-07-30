from arm.logicnode.arm_nodes import *


class SetMapValueNode(ArmLogicTreeNode):
    """Set Map Value.

    @input In: Set the map.

    @input Map: Map to set values.

    @input Key: Key to be set.

    @input Value: Value for the key.
    """

    bl_idname = 'LNSetMapValueNode'
    bl_label = 'Set Map Value'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Map')
        self.add_input('ArmDynamicSocket', 'Key')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
