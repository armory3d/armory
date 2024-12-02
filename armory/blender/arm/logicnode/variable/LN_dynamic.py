from arm.logicnode.arm_nodes import *


class DynamicNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given dynamic value (a value with an arbitrary type) as a variable."""
    bl_idname = 'LNDynamicNode'
    bl_label = 'Dynamic'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Dynamic', is_var=True)
