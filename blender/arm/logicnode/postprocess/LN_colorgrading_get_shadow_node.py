from arm.logicnode.arm_nodes import *

class ColorgradingGetShadowNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNColorgradingGetShadowNode'
    bl_label = 'Colorgrading Get Shadow'
    arm_section = 'colorgrading'
    arm_version = 1

    def init(self, context):
        super(ColorgradingGetShadowNode, self).init(context)
        self.add_output('NodeSocketFloat', 'ShadowMax')
        self.add_output('NodeSocketVector', 'Saturation')
        self.add_output('NodeSocketVector', 'Contrast')
        self.add_output('NodeSocketVector', 'Gamma')
        self.add_output('NodeSocketVector', 'Gain')
        self.add_output('NodeSocketVector', 'Offset')
