from arm.logicnode.arm_nodes import *

class SetVariableNode(ArmLogicTreeNode):
    """Use to set the value of a variable."""
    bl_idname = 'LNSetVariableNode'
    bl_label = 'Set Variable'
    arm_version = 1

    def init(self, context):
        super(SetVariableNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Variable', is_var=True)
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetVariableNode, category=PKG_AS_CATEGORY, section='set')
