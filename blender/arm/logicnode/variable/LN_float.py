from arm.logicnode.arm_nodes import *

class FloatNode(ArmLogicTreeNode):
    """Float node"""
    bl_idname = 'LNFloatNode'
    bl_label = 'Float'
    arm_version = 1

    def init(self, context):
        super(FloatNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Value')
        self.add_output('NodeSocketFloat', 'Float', is_var=True)

add_node(FloatNode, category=PKG_AS_CATEGORY)
