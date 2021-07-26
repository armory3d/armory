from arm.logicnode.arm_nodes import *

class TransformNode(ArmLogicTreeNode):
    """Stores the location, rotation and scale values as a transform."""
    bl_idname = 'LNTransformNode'
    bl_label = 'Transform'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Location')
        self.add_input('ArmVectorSocket', 'Rotation')
        self.add_input('ArmVectorSocket', 'Scale', default_value=[1.0, 1.0, 1.0])

        self.add_output('ArmDynamicSocket', 'Transform')
