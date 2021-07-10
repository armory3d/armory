from arm.logicnode.arm_nodes import *

class SetSceneNode(ArmLogicTreeNode):
    """Sets the active scene."""
    bl_idname = 'LNSetSceneNode'
    bl_label = 'Set Scene Active'
    arm_version = 1

    def init(self, context):
        super(SetSceneNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Scene')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Root')
