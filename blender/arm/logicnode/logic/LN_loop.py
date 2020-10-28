from arm.logicnode.arm_nodes import *

class LoopNode(ArmLogicTreeNode):
    """Resembles a for-loop (`for (i in from...to)`) that is executed at
    once when this node is activated.

    @seeNode While
    @seeNode Loop Break

    @input From: The value to start the loop from (inclusive)
    @input To: The value to end the loop at (exclusive)

    @output Loop: Active at every iteration of the loop
    @output Index: The index for the current iteration
    @output Done: Activated once when the looping is done
    """
    bl_idname = 'LNLoopNode'
    bl_label = 'Loop'
    bl_description = 'Resembles a for-loop that is executed at once when this node is activated'
    arm_section = 'flow'
    arm_version = 1

    def init(self, context):
        super(LoopNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketInt', 'From')
        self.add_input('NodeSocketInt', 'To')
        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('NodeSocketInt', 'Index')
        self.add_output('ArmNodeSocketAction', 'Done')
