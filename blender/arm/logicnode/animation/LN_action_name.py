from arm.logicnode.arm_nodes import *

class ActionNameNode(ArmLogicTreeNode):
    """Stores the given action name."""
    bl_idname = 'LNActionNameNode'
    bl_label = 'Action Name'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAnimAction', 'Action')

        self.add_output('ArmNodeSocketAnimAction', 'Action')
