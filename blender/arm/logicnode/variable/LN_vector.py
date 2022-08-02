from arm.logicnode.arm_nodes import *


class VectorNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given 3D vector as a variable."""
    bl_idname = 'LNVectorNode'
    bl_label = 'Vector'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Z')

        self.add_output('ArmVectorSocket', 'Vector', is_var=True)

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        for i in range(len(self.inputs)):
            self.inputs[i].default_value_raw = master_node.inputs[i].get_default_value()
