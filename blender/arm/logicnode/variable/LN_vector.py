from arm.logicnode.arm_nodes import *

class VectorNode(ArmLogicTreeNode):
    """Stores the given 3D vector as a variable."""
    bl_idname = 'LNVectorNode'
    bl_label = 'Vector'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Z')

        self.add_output('ArmVectorSocket', 'Vector', is_var=True)
