from arm.logicnode.arm_nodes import *

class GetGravityNode(ArmLogicTreeNode):
    """Use to get the world gravity."""
    bl_idname = 'LNGetGravityNode'
    bl_label = 'Get World Gravity'
    arm_version = 1

    def init(self, context):
        super(GetGravityNode, self).init(context)
        self.add_output('NodeSocketVector', 'World Gravity')

add_node(GetGravityNode, category=PKG_AS_CATEGORY)
