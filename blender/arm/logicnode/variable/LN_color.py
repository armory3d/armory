from arm.logicnode.arm_nodes import *


class ColorNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given color as a variable."""
    bl_idname = 'LNColorNode'
    bl_label = 'Color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmColorSocket', 'Color Out', is_var=True)

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.inputs[0].default_value_raw = master_node.inputs[0].get_default_value()
