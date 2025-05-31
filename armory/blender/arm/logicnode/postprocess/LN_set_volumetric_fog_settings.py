from arm.logicnode.arm_nodes import *

class VolumetricFogSetNode(ArmLogicTreeNode):
    """Set the volumetric fog post-processing settings."""
    bl_idname = 'LNVolumetricFogSetNode'
    bl_label = 'Set Volumetric Fog Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmColorSocket', 'Color', default_value=[0.5, 0.6, 0.7, 1.0])
        self.add_input('ArmFloatSocket', 'Amount A', default_value=0.25)
        self.add_input('ArmFloatSocket', 'Amount B', default_value=0.50)

        self.add_output('ArmNodeSocketAction', 'Out')