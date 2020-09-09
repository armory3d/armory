from arm.logicnode.arm_nodes import *

class CanvasSetTextColorNode(ArmLogicTreeNode):
    """Set canvas text color"""
    bl_idname = 'LNCanvasSetTextColorNode'
    bl_label = 'Canvas Set Text Color'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'R')
        self.add_input('NodeSocketFloat', 'G')
        self.add_input('NodeSocketFloat', 'B')
        self.add_input('NodeSocketFloat', 'A')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetTextColorNode, category=PKG_AS_CATEGORY)
