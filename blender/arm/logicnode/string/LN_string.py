from arm.logicnode.arm_nodes import *

class StringNode(ArmLogicTreeNode):
    """Stores a string as a variable."""
    bl_idname = 'LNStringNode'
    bl_label = 'String'
    arm_version = 1

    def init(self, context):
        super(StringNode, self).init(context)
        self.add_input('NodeSocketString', 'String In')
        self.add_output('NodeSocketString', 'String Out', is_var=True)

add_node(StringNode, category=PKG_AS_CATEGORY)
