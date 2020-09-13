from arm.logicnode.arm_nodes import *

class ColorgradingGetHighlightNode(ArmLogicTreeNode):
    """Colorgrading Get Highlight node"""
    bl_idname = 'LNColorgradingGetHighlightNode'
    bl_label = 'Colorgrading Get Highlight'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'HightlightMin')
        self.add_output('NodeSocketVector', 'Saturation')
        self.add_output('NodeSocketVector', 'Contrast')
        self.add_output('NodeSocketVector', 'Gamma')
        self.add_output('NodeSocketVector', 'Gain')
        self.add_output('NodeSocketVector', 'Offset')

add_node(ColorgradingGetHighlightNode, category=PKG_AS_CATEGORY, section='colorgrading')
