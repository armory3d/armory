from arm.logicnode.arm_nodes import *

class BlendActionNode(ArmLogicTreeNode):
    """Interpolates between the two given actions."""
    bl_idname = 'LNBlendActionNode'
    bl_label = 'Blend Action'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action 1')
        self.add_input('ArmNodeSocketAnimAction', 'Action 2')
        self.add_input('ArmFloatSocket', 'Factor', default_value = 0.5)

        self.add_output('ArmNodeSocketAction', 'Out')
