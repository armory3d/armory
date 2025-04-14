from arm.logicnode.arm_nodes import *

class ColorgradingGetShadowNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNColorgradingGetShadowNode'
    bl_label = 'Colorgrading Get Shadow'
    arm_section = 'colorgrading'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'ShadowMax')
        self.add_output('ArmVectorSocket', 'Saturation')
        self.add_output('ArmVectorSocket', 'Contrast')
        self.add_output('ArmVectorSocket', 'Gamma')
        self.add_output('ArmVectorSocket', 'Gain')
        self.add_output('ArmVectorSocket', 'Offset')
