from arm.logicnode.arm_nodes import *


class StringNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given string as a variable."""
    bl_idname = 'LNStringNode'
    bl_label = 'String'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'String In')

        self.add_output('ArmStringSocket', 'String Out', is_var=True)

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.inputs[0].default_value_raw = master_node.inputs[0].get_default_value()
