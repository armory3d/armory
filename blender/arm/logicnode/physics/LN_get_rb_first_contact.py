from arm.logicnode.arm_nodes import *

class GetFirstContactNode(ArmLogicTreeNode):
    """Returns the first object that is colliding with the given object.

    @seeNode Get Contacts
    """
    bl_idname = 'LNGetFirstContactNode'
    bl_label = 'Get RB First Contact'
    arm_version = 1

    def init(self, context):
        super(GetFirstContactNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_output('ArmNodeSocketObject', 'First Contact')

add_node(GetFirstContactNode, category=PKG_AS_CATEGORY, section='contact')
