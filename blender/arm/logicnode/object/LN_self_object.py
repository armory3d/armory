from arm.logicnode.arm_nodes import *

class SelfObjectNode(ArmLogicTreeNode):
    """Returns the object that owns the trait."""
    bl_idname = 'LNSelfNode'
    bl_label = 'Self Object'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')
