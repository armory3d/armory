from arm.logicnode.arm_nodes import *

class SelectOutputNode(ArmLogicTreeNode):
    """Selects one of multiple outputs depending on the index

    @input In: Action input.

    @input Index: Output index to run.

    @output Default: Run if output index not present.
    """

    bl_idname = 'LNSelectOutputNode'
    bl_label = 'Select output'
    arm_version = 1
    min_outputs = 2

    def __init__(self):
        super(SelectOutputNode, self).__init__()
        array_nodes[self.get_id_str()] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmIntSocket', 'Index')

        self.add_output('ArmNodeSocketAction', 'Default')
        self.add_output('ArmNodeSocketAction', 'Index 0')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_output', text='New', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.socket_type = 'ArmNodeSocketAction'
        op.name_format = 'Index {0}'
        op.index_name_offset = -1
        column = row.column(align=True)
        op = column.operator('arm.node_remove_output', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        if len(self.outputs) == self.min_outputs:
            column.enabled = False
