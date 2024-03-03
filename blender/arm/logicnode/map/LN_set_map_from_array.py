from arm.logicnode.arm_nodes import *


class SetMapFromArrayNode(ArmLogicTreeNode):
    """Set Map From Arrays

    @input In: Set the map.

    @input Map: Map to set values.

    @input Key: Array of keys to be set.

    @input Value: Array of corresponding values for the keys.
    """

    bl_idname = 'LNSetMapFromArrayNode'
    bl_label = 'Set Map From Array'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Map')
        self.add_input('ArmNodeSocketArray', 'Keys')
        self.add_input('ArmNodeSocketArray', 'Values')

        self.add_output('ArmNodeSocketAction', 'Out')
