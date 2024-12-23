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

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmIntSocket', 'From')
        self.add_input('ArmIntSocket', 'To')

        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('ArmIntSocket', 'Index')
        self.add_output('ArmNodeSocketAction', 'Done')

    def draw_label(self) -> str:
        inp_from = self.inputs['From']
        inp_to = self.inputs['To']
        if inp_from.is_linked and inp_to.is_linked:
            return self.bl_label

        val_from = 'x' if inp_from.is_linked else inp_from.default_value_raw
        val_to = 'y' if inp_to.is_linked else inp_to.default_value_raw

        return f'{self.bl_label}: {val_from}...{val_to}'
