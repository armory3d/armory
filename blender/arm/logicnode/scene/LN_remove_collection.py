from arm.logicnode.arm_nodes import *

class RemoveGroupNode(ArmLogicTreeNode):
    """Removes the given collection from the scene."""
    bl_idname = 'LNRemoveGroupNode'
    bl_label = 'Remove Collection'
    arm_section = 'collection'
    arm_version = 1

    def init(self, context):
        super(RemoveGroupNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Collection')

        self.add_output('ArmNodeSocketAction', 'Out')
