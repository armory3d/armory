from arm.logicnode.arm_nodes import *

class CanvasGetScaleNode(ArmLogicTreeNode):
    """Use to get the scale of an UI element."""
    bl_idname = 'LNCanvasGetScaleNode'
    bl_label = 'Get Canvas Scale'
    arm_version = 1

    def init(self, context):
        super(CanvasGetScaleNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketInt', 'Height')
        self.add_output('NodeSocketInt', 'Width')

add_node(CanvasGetScaleNode, category=PKG_AS_CATEGORY)
