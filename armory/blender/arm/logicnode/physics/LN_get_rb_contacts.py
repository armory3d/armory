from arm.logicnode.arm_nodes import *

class GetContactsNode(ArmLogicTreeNode):
    """Returns an array with all objects that are colliding with the
    given object.

    @seeNode Get First Contact
    """
    bl_idname = 'LNGetContactsNode'
    bl_label = 'Get RB Contacts'
    arm_section = 'contact'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'RB')

        self.add_output('ArmNodeSocketArray', 'Contacts')
