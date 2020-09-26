from arm.logicnode.arm_nodes import *

class CanvasSetTextColorNode(ArmLogicTreeNode):
    """Use to set an UI text color."""
    bl_idname = 'LNCanvasSetTextColorNode'
    bl_label = 'Set Canvas Text Color'
    arm_version = 1

    def init(self, context):
        super(CanvasSetTextColorNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'R')
        self.add_input('NodeSocketFloat', 'G')
        self.add_input('NodeSocketFloat', 'B')
        self.add_input('NodeSocketFloat', 'A')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetTextColorNode, category=PKG_AS_CATEGORY)
