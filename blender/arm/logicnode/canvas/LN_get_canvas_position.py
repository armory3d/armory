from arm.logicnode.arm_nodes import *

class CanvasGetPositionNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNCanvasGetPositionNode'
    bl_label = 'Get Canvas Position'
    arm_version = 1

    def init(self, context):
        super(CanvasGetPositionNode, self).init(context)
        self.add_input('NodeSocketString', 'Element')

        self.add_output('NodeSocketInt', 'Position')
