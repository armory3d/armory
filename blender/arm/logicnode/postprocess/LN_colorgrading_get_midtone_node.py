from arm.logicnode.arm_nodes import *

class ColorgradingGetMidtoneNode(ArmLogicTreeNode):
    """Colorgrading Get Midtone node"""
    bl_idname = 'LNColorgradingGetMidtoneNode'
    bl_label = 'Colorgrading Get Midtone'

    def init(self, context):
        self.add_output('NodeSocketVector', 'Saturation')
        self.add_output('NodeSocketVector', 'Contrast')
        self.add_output('NodeSocketVector', 'Gamma')
        self.add_output('NodeSocketVector', 'Gain')
        self.add_output('NodeSocketVector', 'Offset')

add_node(ColorgradingGetMidtoneNode, category=PKG_AS_CATEGORY, section='colorgrading')
