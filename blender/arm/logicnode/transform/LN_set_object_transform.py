from arm.logicnode.arm_nodes import *

class SetTransformNode(ArmLogicTreeNode):
    """Sets the transform of the given object."""
    bl_idname = 'LNSetTransformNode'
    bl_label = 'Set Object Transform'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmNodeSocketAction', 'Out')
