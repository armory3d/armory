from arm.logicnode.arm_nodes import *

class OnInitNode(ArmLogicTreeNode):
    """Activates the output on the first frame of execution of the logic tree."""
    bl_idname = 'LNOnInitNode'
    bl_label = 'On Init'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
