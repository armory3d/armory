from arm.logicnode.arm_nodes import *

class CanvasSetRotationNode(ArmLogicTreeNode):
    """Sets the rotation of the given UI element."""
    bl_idname = 'LNCanvasSetRotationNode'
    bl_label = 'Set Canvas Rotation'
    arm_version = 1

    def init(self, context):
        super(CanvasSetRotationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'Rad')

        self.add_output('ArmNodeSocketAction', 'Out')
