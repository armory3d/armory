from arm.logicnode.arm_nodes import *

class SwitchNode(ArmLogicTreeNode):
    """Activates the outputs depending of the value. If the "value" is equal to "case 1", the output "case 1" will be activated.

    @output Default: Activated if the input value does not match any case.
    """
    bl_idname = 'LNSwitchNode'
    bl_label = 'Switch Output'
    arm_version = 1
    min_inputs = 2
    min_outputs = 1

    def __init__(self):
        super(SwitchNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Default')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input_output', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.in_socket_type = 'ArmDynamicSocket'
        op.out_socket_type = 'ArmNodeSocketAction'
        op.in_name_format = 'Case {0}'
        op.out_name_format = 'Case {0}'
        op.in_index_name_offset = -1
        op2 = row.operator('arm.node_remove_input_output', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
