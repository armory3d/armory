from arm.logicnode.arm_nodes import *

class RemoveActiveSceneNode(ArmLogicTreeNode):
    """Removes the active scene."""
    bl_idname = 'LNRemoveActiveSceneNode'
    bl_label = 'Remove Scene Active'
    arm_version = 1

    def init(self, context):
        super(RemoveActiveSceneNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')
