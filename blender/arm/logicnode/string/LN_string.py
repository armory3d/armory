from arm.logicnode.arm_nodes import *

class StringNode(ArmLogicTreeNode):
    """Stores the given string as a variable."""
    bl_idname = 'LNStringNode'
    bl_label = 'String'
    arm_version = 1

    def init(self, context):
        super(StringNode, self).init(context)
        self.add_input('NodeSocketString', 'String In')
        self.add_output('NodeSocketString', 'String Out', is_var=True)
