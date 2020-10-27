from arm.logicnode.arm_nodes import *

class ColorgradingGetGlobalNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNColorgradingGetGlobalNode'
    bl_label = 'Colorgrading Get Global'
    arm_section = 'colorgrading'
    arm_version = 1

    def init(self, context):
        super(ColorgradingGetGlobalNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Whitebalance')
        self.add_output('NodeSocketVector', 'Tint')
        self.add_output('NodeSocketVector', 'Saturation')
        self.add_output('NodeSocketVector', 'Contrast')
        self.add_output('NodeSocketVector', 'Gamma')
        self.add_output('NodeSocketVector', 'Gain')
        self.add_output('NodeSocketVector', 'Offset')
