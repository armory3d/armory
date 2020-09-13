from arm.logicnode.arm_nodes import *

class StringNode(ArmLogicTreeNode):
    """String node"""
    bl_idname = 'LNStringNode'
    bl_label = 'String'
    arm_version = 1

    def init(self, context):
        super(StringNode, self).init(context)
        self.add_input('NodeSocketString', 'Value')
        self.add_output('NodeSocketString', 'String', is_var=True)

add_node(StringNode, category=PKG_AS_CATEGORY)
