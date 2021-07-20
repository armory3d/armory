from arm.logicnode.arm_nodes import *

class SetGravityNode(ArmLogicTreeNode):
    """Sets the world gravity.

    @seeNode Get World Gravity
    """
    bl_idname = 'LNSetGravityNode'
    bl_label = 'Set World Gravity'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmVectorSocket', 'Gravity')

        self.add_output('ArmNodeSocketAction', 'Out')
