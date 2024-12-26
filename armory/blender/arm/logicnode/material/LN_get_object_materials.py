from arm.logicnode.arm_nodes import *

class GetMaterialNode(ArmLogicTreeNode):
    """Returns the material of the given object."""
    bl_idname = 'LNGetMaterialNode'
    bl_label = 'Get Object Material'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmIntSocket', 'Slot')

        self.add_output('ArmDynamicSocket', 'Material')
