from arm.logicnode.arm_nodes import *

class SetVariableNode(ArmLogicTreeNode):
    """Sets the value of the given variable.

    @input Variable: this socket must be connected to a variable node
        (recognized by the little dot inside the socket). The value that
        is stored inside the connected node is changed upon activation.
    @input Value: the value that should be written into the variable.
    """
    bl_idname = 'LNSetVariableNode'
    bl_label = 'Set Variable'
    arm_section = 'set'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Variable', is_var=True)
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
