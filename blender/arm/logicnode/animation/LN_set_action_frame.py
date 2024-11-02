from arm.logicnode.arm_nodes import *

class SetActionFrameNode(ArmLogicTreeNode):
    """Sets the current action frame for the given object."""
    bl_idname = 'LNSetActionFrameNode'
    bl_label = 'Set Action Frame'
    bl_width_default = 200
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action ID')
        self.add_input('ArmIntSocket', 'Frame')

        self.add_output('ArmNodeSocketAction', 'Out')