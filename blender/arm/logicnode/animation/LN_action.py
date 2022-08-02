from arm.logicnode.arm_nodes import *

class AnimActionNode(ArmLogicTreeNode):
    """Stores the given action as a variable."""
    bl_idname = 'LNAnimActionNode'
    bl_label = 'Action'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAnimAction', 'Action')

        self.add_output('ArmNodeSocketAnimAction', 'Action', is_var=True)
