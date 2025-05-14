from arm.logicnode.arm_nodes import *

class GetGravityNode(ArmLogicTreeNode):
    """Returns the world gravity.

    @seeNode Set Gravity
    """
    bl_idname = 'LNGetGravityNode'
    bl_label = 'Get World Gravity'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmVectorSocket', 'World Gravity')
