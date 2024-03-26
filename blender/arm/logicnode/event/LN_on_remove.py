from arm.logicnode.arm_nodes import *

class OnRemoveNode(ArmLogicTreeNode):
    """Activates the output when logic tree is removed"""
    bl_idname = 'LNOnRemoveNode'
    bl_label = 'On Remove'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
