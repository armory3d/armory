from arm.logicnode.arm_nodes import *


class BooleanNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given boolean as a variable. A boolean value has just two
    states: `true` and `false`."""
    bl_idname = 'LNBooleanNode'
    bl_label = 'Boolean'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmBoolSocket', 'Bool In')

        self.add_output('ArmBoolSocket', 'Bool Out', is_var=True)

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.inputs[0].default_value_raw = master_node.inputs[0].get_default_value()
