from arm.logicnode.arm_nodes import *

class CanvasGetSliderNode(ArmLogicTreeNode):
    """Returns the value of the given UI slider."""
    bl_idname = 'LNCanvasGetSliderNode'
    bl_label = 'Get Canvas Slider'
    arm_version = 1

    def init(self, context):
        super(CanvasGetSliderNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')

        self.add_output('NodeSocketFloat', 'Float')
