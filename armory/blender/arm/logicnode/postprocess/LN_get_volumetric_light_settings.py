from arm.logicnode.arm_nodes import *

class VolumetricLightGetNode(ArmLogicTreeNode):
    """Returns the volumetric light post-processing settings."""
    bl_idname = 'LNVolumetricLightGetNode'
    bl_label = 'Get Volumetric Light Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmColorSocket', 'Air Color')
        self.add_output('ArmFloatSocket', 'Air Turbidity')
        self.add_output('ArmIntSocket', 'Steps')
