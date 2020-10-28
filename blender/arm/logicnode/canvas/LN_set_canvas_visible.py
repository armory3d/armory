from arm.logicnode.arm_nodes import *

class CanvasSetVisibleNode(ArmLogicTreeNode):
    """Sets whether the given UI element is visibile."""
    bl_idname = 'LNCanvasSetVisibleNode'
    bl_label = 'Set Canvas Visible'
    arm_version = 1

    def init(self, context):
        super(CanvasSetVisibleNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketBool', 'Visible')
        self.add_output('ArmNodeSocketAction', 'Out')
