from arm.logicnode.arm_nodes import *

class WhileNode(ArmLogicTreeNode):
    """Loops while the condition is `true`.

    @seeNode Loop
    @seeNode Loop Break

    @input Condition: boolean that resembles the result of the condition

    @output Loop: Activated on every iteration step
    @output Done: Activated when the loop is done executing"""
    bl_idname = 'LNWhileNode'
    bl_label = 'While True'
    arm_section = 'flow'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Condition')

        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('ArmNodeSocketAction', 'Done')
