from arm.logicnode.arm_nodes import *

class CanvasGetSliderNode(ArmLogicTreeNode):
    """Set canvas text"""
    bl_idname = 'LNCanvasGetSliderNode'
    bl_label = 'Canvas Get Slider'
    arm_version = 1

    def init(self, context):
        super(CanvasGetSliderNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')
        self.add_output('NodeSocketFloat', 'Value')

add_node(CanvasGetSliderNode, category=PKG_AS_CATEGORY)
