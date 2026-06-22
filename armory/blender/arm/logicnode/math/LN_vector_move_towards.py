from arm.logicnode.arm_nodes import *

class VectorMoveTowardsNode(ArmLogicTreeNode):
    """Add a constant value to the given vector until it reach the target vector."""
    bl_idname = 'LNVectorMoveTowardsNode'
    bl_label = 'Vector Move Towards'
    arm_section = 'vector'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Vector 1', default_value=[0.0, 0.0, 0.0])
        self.add_input('ArmVectorSocket', 'Vector 2', default_value=[1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Delta', default_value=0.1)

        self.add_output('ArmVectorSocket', 'Result')