from arm.logicnode.arm_nodes import *

class PromptNode(ArmLogicTreeNode):
    """Open a prompt with the give string value an returns either the user value
    or the default string if specified (works only for web browsers).

    @input String: message to display.
    @input Default: default string value in case there is no user input.

    @output String: user input value or default value in case is specified.
    """
    bl_idname = 'LNPromptNode'
    bl_label = 'Prompt'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmStringSocket', 'Default')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmStringSocket', 'String')
