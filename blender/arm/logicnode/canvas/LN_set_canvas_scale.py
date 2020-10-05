from arm.logicnode.arm_nodes import *

class CanvasSetScaleNode(ArmLogicTreeNode):
    """Sets the scale of the given UI element."""
    bl_idname = 'LNCanvasSetScaleNode'
    bl_label = 'Set Canvas Scale'
    arm_version = 1

    def init(self, context):
        super(CanvasSetScaleNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketInt', 'Height')
        self.add_input('NodeSocketInt', 'Width')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetScaleNode, category=PKG_AS_CATEGORY)
