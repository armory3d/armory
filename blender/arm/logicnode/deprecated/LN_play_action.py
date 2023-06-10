from arm.logicnode.arm_nodes import *


@deprecated('Play Action From')
class PlayActionNode(ArmLogicTreeNode):
    """Plays the given action."""
    bl_idname = 'LNPlayActionNode'
    bl_label = 'Play Action'
    bl_description = "Please use the \"Play Action From\" node instead"
    arm_category = 'Animation'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_input('ArmFloatSocket', 'Blend', default_value=0.2)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')
