from arm.logicnode.arm_nodes import *

class SeparateTransformNode(ArmLogicTreeNode):
    """Separates the transform of the given object."""
    bl_idname = 'LNSeparateTransformNode'
    bl_label = 'Separate Transform'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmVectorSocket', 'Location')
        self.add_output('ArmVectorSocket', 'Rotation')
        self.add_output('ArmVectorSocket', 'Scale')
