from arm.logicnode.arm_nodes import *

class GetSystemLanguage(ArmLogicTreeNode):
    """Returns the name of the current system."""
    bl_idname = 'LNGetSystemLanguage'
    bl_label = 'Get System Language'
    arm_version = 1

    def init(self, context):
        super(GetSystemLanguage, self).init(context)
        self.add_output('NodeSocketString', 'Language')

add_node(GetSystemLanguage, category=PKG_AS_CATEGORY, section='Native')
