from arm.logicnode.arm_nodes import *

class SwitchActionMultiNode(ArmLogicTreeNode):
    """Switch between the given actions with interpolation."""
    bl_idname = 'LNSwitchActionMultiNode'
    bl_label = 'Switch Action Multi'
    arm_version = 1
    min_inputs = 8

    def __init__(self):
        super(SwitchActionMultiNode, self).__init__()
        array_nodes[self.get_id_str()] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Switch')
        self.add_input('ArmIntSocket', 'Switch To', default_value = 1)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Restart', default_value = True)
        self.add_input('ArmFloatSocket', 'Time', default_value = 1.0)
        self.add_input('ArmIntSocket', 'Bone Group', default_value = -1)
        self.add_input('ArmNodeSocketAnimTree', 'Action 0')
        self.add_input('ArmNodeSocketAnimTree', 'Action 1')

        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('ArmNodeSocketAnimTree', 'Result')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.socket_type = 'ArmNodeSocketAnimTree'
        op.name_format = 'Action {0}'
        op.index_name_offset = -6
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        if len(self.inputs) == self.min_inputs:
            column.enabled = False