from arm.logicnode.arm_nodes import *

class BooleanNode(ArmLogicTreeNode):
    """Use to hold a boolean as a variable."""
    bl_idname = 'LNBooleanNode'
    bl_label = 'Boolean'
    arm_version = 1

    def init(self, context):
        super(BooleanNode, self).init(context)
        self.add_input('NodeSocketBool', 'Bool In')
        self.add_output('NodeSocketBool', 'Bool Out', is_var=True)

add_node(BooleanNode, category=PKG_AS_CATEGORY)
