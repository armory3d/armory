from arm.logicnode.arm_nodes import *

class NoneNode(ArmLogicTreeNode):
    """A `null` value that can be used in comparisons and conditions."""
    bl_idname = 'LNNoneNode'
    bl_label = 'Null'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Null')
