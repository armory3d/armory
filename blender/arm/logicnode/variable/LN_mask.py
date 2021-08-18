from arm.logicnode.arm_nodes import *

class MaskNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNMaskNode'
    bl_label = 'Mask'
    arm_version = 1

    def arm_init(self, context):
        for i in range(1, 21):
            label = 'Group {:02d}'.format(i)
            self.inputs.new('ArmBoolSocket', label)

        self.add_output('ArmIntSocket', 'Mask', is_var=True)
