from arm.logicnode.arm_nodes import *

class BooleanNode(ArmLogicTreeNode):
    """Bool node"""
    bl_idname = 'LNBooleanNode'
    bl_label = 'Boolean'

    def init(self, context):
        self.add_input('NodeSocketBool', 'Value')
        self.add_output('NodeSocketBool', 'Bool', is_var=True)

add_node(BooleanNode, category=PKG_AS_CATEGORY)
