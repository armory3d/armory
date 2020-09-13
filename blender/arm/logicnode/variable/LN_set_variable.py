from arm.logicnode.arm_nodes import *

class SetVariableNode(ArmLogicTreeNode):
    """Set variable node"""
    bl_idname = 'LNSetVariableNode'
    bl_label = 'Set Variable'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Variable', is_var=True)
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetVariableNode, category=PKG_AS_CATEGORY, section='set')
