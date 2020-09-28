from arm.logicnode.arm_nodes import *

class IntegerNode(ArmLogicTreeNode):
    """Stores an integer (a whole number) as a variable."""
    bl_idname = 'LNIntegerNode'
    bl_label = 'Integer'
    arm_version = 1

    def init(self, context):
        super(IntegerNode, self).init(context)
        self.add_input('NodeSocketInt', 'Int In')
        self.add_output('NodeSocketInt', 'Int Out', is_var=True)

add_node(IntegerNode, category=PKG_AS_CATEGORY)
