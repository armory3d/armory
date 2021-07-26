from arm.logicnode.arm_nodes import *

class VectorClampToSizeNode(ArmLogicTreeNode):
    """Keeps the vector value inside the given range."""
    bl_idname = 'LNVectorClampToSizeNode'
    bl_label = 'Vector Clamp'
    arm_section = 'vector'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Vector In', default_value=[0.0, 0.0, 0.0])
        self.add_input('ArmFloatSocket', 'Min')
        self.add_input('ArmFloatSocket', 'Max')

        self.add_output('ArmVectorSocket', 'Vector Out')
