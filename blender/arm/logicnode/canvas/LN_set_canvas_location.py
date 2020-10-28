from arm.logicnode.arm_nodes import *

class CanvasSetLocationNode(ArmLogicTreeNode):
    """Sets the location of the given UI element."""
    bl_idname = 'LNCanvasSetLocationNode'
    bl_label = 'Set Canvas Location'
    arm_version = 1

    def init(self, context):
        super(CanvasSetLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'X')
        self.add_input('NodeSocketFloat', 'Y')
        self.add_output('ArmNodeSocketAction', 'Out')
