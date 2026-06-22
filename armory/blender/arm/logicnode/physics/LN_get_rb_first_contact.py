from arm.logicnode.arm_nodes import *

class GetFirstContactNode(ArmLogicTreeNode):
    """Returns the first object that is colliding with the given object.

    @seeNode Get Contacts
    """
    bl_idname = 'LNGetFirstContactNode'
    bl_label = 'Get RB First Contact'
    arm_section = 'contact'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'RB')

        self.add_output('ArmNodeSocketObject', 'First Contact')
