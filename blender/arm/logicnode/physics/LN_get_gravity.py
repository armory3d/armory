from arm.logicnode.arm_nodes import *

class GetGravityNode(ArmLogicTreeNode):
    """Get Gravity node"""
    bl_idname = 'LNGetGravityNode'
    bl_label = 'Get Gravity'

    def init(self, context):
        self.add_input('NodeSocketVector', 'Gravity')

add_node(GetGravityNode, category=PKG_AS_CATEGORY)
