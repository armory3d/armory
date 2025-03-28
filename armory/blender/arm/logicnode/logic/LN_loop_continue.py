from arm.logicnode.arm_nodes import *

class LoopContinueNode(ArmLogicTreeNode):
    """continues to the next loop.

    @seeNode Loop
    @seeNode While
    """
    bl_idname = 'LNLoopContinueNode'
    bl_label = 'Loop Continue'
    arm_section = 'flow'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
