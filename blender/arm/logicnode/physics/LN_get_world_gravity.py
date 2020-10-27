from arm.logicnode.arm_nodes import *

class GetGravityNode(ArmLogicTreeNode):
    """Returns the world gravity.

    @seeNode Set Gravity
    """
    bl_idname = 'LNGetGravityNode'
    bl_label = 'Get World Gravity'
    arm_version = 1

    def init(self, context):
        super(GetGravityNode, self).init(context)
        self.add_output('NodeSocketVector', 'World Gravity')
