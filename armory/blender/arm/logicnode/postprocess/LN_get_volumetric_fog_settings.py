from arm.logicnode.arm_nodes import *

class VolumetricFogGetNode(ArmLogicTreeNode):
    """Returns the volumetric fog post-processing settings."""
    bl_idname = 'LNVolumetricFogGetNode'
    bl_label = 'Get Volumetric Fog Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmColorSocket', 'Color')
        self.add_output('ArmFloatSocket', 'Amount A')
        self.add_output('ArmFloatSocket', 'Amount B')
