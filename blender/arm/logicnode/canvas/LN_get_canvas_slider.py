from arm.logicnode.arm_nodes import *

class CanvasGetSliderNode(ArmLogicTreeNode):
    """Use to get the value of an UI slider."""
    bl_idname = 'LNCanvasGetSliderNode'
    bl_label = 'Get Canvas Slider'
    arm_version = 1

    def init(self, context):
        super(CanvasGetSliderNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketFloat', 'Float')

add_node(CanvasGetSliderNode, category=PKG_AS_CATEGORY)
