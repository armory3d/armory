from arm.logicnode.arm_nodes import *

class ColorgradingGetMidtoneNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNColorgradingGetMidtoneNode'
    bl_label = 'Colorgrading Get Midtone'
    arm_section = 'colorgrading'
    arm_version = 1

    def init(self, context):
        super(ColorgradingGetMidtoneNode, self).init(context)
        self.add_output('NodeSocketVector', 'Saturation')
        self.add_output('NodeSocketVector', 'Contrast')
        self.add_output('NodeSocketVector', 'Gamma')
        self.add_output('NodeSocketVector', 'Gain')
        self.add_output('NodeSocketVector', 'Offset')
