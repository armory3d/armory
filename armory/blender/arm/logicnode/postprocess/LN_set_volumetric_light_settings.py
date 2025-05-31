from arm.logicnode.arm_nodes import *

class VolumetricLightSetNode(ArmLogicTreeNode):
    """Set the volumetric light post-processing settings."""
    bl_idname = 'LNVolumetricLightSetNode'
    bl_label = 'Set Volumetric Light Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmColorSocket', 'Air Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Air Turbidity', default_value=1)
        self.add_input('ArmIntSocket', 'Steps', default_value=20)

        self.add_output('ArmNodeSocketAction', 'Out')