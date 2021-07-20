from arm.logicnode.arm_nodes import *

class SetMaterialSlotNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNSetMaterialSlotNode'
    bl_label = 'Set Object Material Slot'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmDynamicSocket', 'Material')
        self.add_input('ArmIntSocket', 'Slot')

        self.add_output('ArmNodeSocketAction', 'Out')
