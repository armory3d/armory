from arm.logicnode.arm_nodes import *

class ColorgradingGetGlobalNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNColorgradingGetGlobalNode'
    bl_label = 'Colorgrading Get Global'
    arm_section = 'colorgrading'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Whitebalance')
        self.add_output('ArmVectorSocket', 'Tint')
        self.add_output('ArmVectorSocket', 'Saturation')
        self.add_output('ArmVectorSocket', 'Contrast')
        self.add_output('ArmVectorSocket', 'Gamma')
        self.add_output('ArmVectorSocket', 'Gain')
        self.add_output('ArmVectorSocket', 'Offset')
