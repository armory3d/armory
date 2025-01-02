from arm.logicnode.arm_nodes import *

class ClearParentNode(ArmLogicTreeNode):
    """Removes the parent of the given object."""
    bl_idname = 'LNClearParentNode'
    bl_label = 'Remove Object Parent'
    arm_section = 'relations'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Keep Transform', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Out')
