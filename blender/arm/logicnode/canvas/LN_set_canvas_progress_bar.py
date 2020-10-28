from arm.logicnode.arm_nodes import *

class CanvasSetPBNode(ArmLogicTreeNode):
    """Sets the value of the given UI progress bar."""
    bl_idname = 'LNCanvasSetPBNode'
    bl_label = 'Set Canvas Progress Bar'
    arm_version = 1

    def init(self, context):
        super(CanvasSetPBNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketInt', 'At')
        self.add_input('NodeSocketInt', 'Max')
        self.add_output('ArmNodeSocketAction', 'Out')
