from arm.logicnode.arm_nodes import *

class ColorNode(ArmLogicTreeNode):
    """Stores the given color as a variable."""
    bl_idname = 'LNColorNode'
    bl_label = 'Color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmColorSocket', 'Color Out', is_var=True)
