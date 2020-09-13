from arm.logicnode.arm_nodes import *

class ColorgradingGetShadowNode(ArmLogicTreeNode):
    """Colorgrading Get Shadow node"""
    bl_idname = 'LNColorgradingGetShadowNode'
    bl_label = 'Colorgrading Get Shadow'
    arm_version = 1

    def init(self, context):
        super(ColorgradingGetShadowNode, self).init(context)
        self.add_output('NodeSocketFloat', 'ShadowMax')
        self.add_output('NodeSocketVector', 'Saturation')
        self.add_output('NodeSocketVector', 'Contrast')
        self.add_output('NodeSocketVector', 'Gamma')
        self.add_output('NodeSocketVector', 'Gain')
        self.add_output('NodeSocketVector', 'Offset')

add_node(ColorgradingGetShadowNode, category=PKG_AS_CATEGORY, section='colorgrading')
