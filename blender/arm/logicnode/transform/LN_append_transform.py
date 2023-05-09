from arm.logicnode.arm_nodes import *

class AppendTransformNode(ArmLogicTreeNode):
    """Appends transform to the given object."""
    bl_idname = 'LNAppendTransformNode'
    bl_label = 'Append Transform'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmNodeSocketAction', 'Out')
