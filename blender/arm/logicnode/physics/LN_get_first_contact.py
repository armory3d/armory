from arm.logicnode.arm_nodes import *

class GetFirstContactNode(ArmLogicTreeNode):
    """Use to get the first contact of a rigid body."""
    bl_idname = 'LNGetFirstContactNode'
    bl_label = 'Get First Contact'
    arm_version = 1

    def init(self, context):
        super(GetFirstContactNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_output('ArmNodeSocketObject', 'First Contact')

add_node(GetFirstContactNode, category=PKG_AS_CATEGORY, section='contact')
