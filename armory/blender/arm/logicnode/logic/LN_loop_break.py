from arm.logicnode.arm_nodes import *

class LoopBreakNode(ArmLogicTreeNode):
    """Terminates the currently executing loop (only one loop is
    executed at once).

    @seeNode Loop
    @seeNode While
    """
    bl_idname = 'LNLoopBreakNode'
    bl_label = 'Loop Break'
    arm_section = 'flow'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
