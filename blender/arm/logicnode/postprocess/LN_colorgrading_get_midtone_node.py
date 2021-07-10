from arm.logicnode.arm_nodes import *

class ColorgradingGetMidtoneNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNColorgradingGetMidtoneNode'
    bl_label = 'Colorgrading Get Midtone'
    arm_section = 'colorgrading'
    arm_version = 1

    def init(self, context):
        super(ColorgradingGetMidtoneNode, self).init(context)
        self.add_output('ArmVectorSocket', 'Saturation')
        self.add_output('ArmVectorSocket', 'Contrast')
        self.add_output('ArmVectorSocket', 'Gamma')
        self.add_output('ArmVectorSocket', 'Gain')
        self.add_output('ArmVectorSocket', 'Offset')
