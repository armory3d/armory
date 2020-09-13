from arm.logicnode.arm_nodes import *

class IntegerNode(ArmLogicTreeNode):
    """Int node"""
    bl_idname = 'LNIntegerNode'
    bl_label = 'Integer'
    arm_version = 1

    def init(self, context):
        super(IntegerNode, self).init(context)
        self.add_input('NodeSocketInt', 'Value')
        self.add_output('NodeSocketInt', 'Int', is_var=True)

add_node(IntegerNode, category=PKG_AS_CATEGORY)
