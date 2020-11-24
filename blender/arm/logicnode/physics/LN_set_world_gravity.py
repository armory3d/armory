from arm.logicnode.arm_nodes import *

class SetGravityNode(ArmLogicTreeNode):
    """Sets the world gravity.

    @seeNode Get World Gravity
    """
    bl_idname = 'LNSetGravityNode'
    bl_label = 'Set World Gravity'
    arm_version = 1

    def init(self, context):
        super(SetGravityNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketVector', 'Gravity')

        self.add_output('ArmNodeSocketAction', 'Out')
