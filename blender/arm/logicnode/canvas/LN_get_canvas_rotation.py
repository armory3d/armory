from arm.logicnode.arm_nodes import *

class CanvasGetRotationNode(ArmLogicTreeNode):
    """Returns the rotation of the given UI element."""
    bl_idname = 'LNCanvasGetRotationNode'
    bl_label = 'Get Canvas Rotation'
    arm_version = 1

    def init(self, context):
        super(CanvasGetRotationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketFloat', 'Rad')
