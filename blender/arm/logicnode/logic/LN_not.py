from arm.logicnode.arm_nodes import *

class NotNode(ArmLogicTreeNode):
    """Use to invert a boolean value."""
    bl_idname = 'LNNotNode'
    bl_label = 'Not'
    arm_version = 1

    def init(self, context):
        super(NotNode, self).init(context)
        self.add_input('NodeSocketBool', 'Bool In')
        self.add_output('NodeSocketBool', 'Bool Out')

add_node(NotNode, category=PKG_AS_CATEGORY)
