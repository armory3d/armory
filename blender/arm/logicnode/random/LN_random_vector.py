from arm.logicnode.arm_nodes import *


class RandomVectorNode(ArmLogicTreeNode):
    """Generates a random vector."""
    bl_idname = 'LNRandomVectorNode'
    bl_label = 'Random Vector'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Min', default_value=[-1.0, -1.0, -1.0])
        self.add_input('ArmVectorSocket', 'Max', default_value=[1.0, 1.0, 1.0])
        self.add_output('ArmVectorSocket', 'Vector')
