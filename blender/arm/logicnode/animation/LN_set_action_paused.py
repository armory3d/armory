from arm.logicnode.arm_nodes import *

class SetActionPausedNode(ArmLogicTreeNode):
    """Sets the action paused state of the given object."""
    bl_idname = 'LNSetActionPausedNode'
    bl_label = 'Set Action Paused'
    arm_version = 1

    def init(self, context):
        super(SetActionPausedNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Paused')

        self.add_output('ArmNodeSocketAction', 'Out')
