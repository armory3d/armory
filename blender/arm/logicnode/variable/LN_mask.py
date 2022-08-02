from arm.logicnode.arm_nodes import *


class MaskNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNMaskNode'
    bl_label = 'Mask'
    arm_version = 1

    def arm_init(self, context):
        for i in range(1, 21):
            label = 'Group {:02d}'.format(i)
            self.inputs.new('ArmBoolSocket', label)

        self.add_output('ArmIntSocket', 'Mask', is_var=True)

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        for i in range(len(self.inputs)):
            self.inputs[i].default_value_raw = master_node.inputs[i].get_default_value()
