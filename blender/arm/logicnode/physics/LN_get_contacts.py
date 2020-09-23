from arm.logicnode.arm_nodes import *

class GetContactsNode(ArmLogicTreeNode):
    """Use to get the contacts of a rigid body."""
    bl_idname = 'LNGetContactsNode'
    bl_label = 'Get Contacts'
    arm_version = 1

    def init(self, context):
        super(GetContactsNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_output('ArmNodeSocketArray', 'Contacts')

add_node(GetContactsNode, category=PKG_AS_CATEGORY, section='contact')
