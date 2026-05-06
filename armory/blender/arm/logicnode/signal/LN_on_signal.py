from arm.logicnode.arm_nodes import *


class OnSignalNode(ArmLogicTreeNode):
    """Activates the output when the given Signal emits.

    Connect a Signal instance to the input. When that Signal emits,
    the output is activated and emitted arguments are available on
    the dynamic output sockets.

    Use 'Add Arg' to add output sockets for receiving emitted data.

    @seeNode Signal
    @seeNode Emit Signal"""

    bl_idname = 'LNOnSignalNode'
    bl_label = 'On Signal'
    arm_version = 1
    arm_section = 'signal'
    min_outputs = 1


    def __init__(self, *args, **kwargs):
        super(OnSignalNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self


    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Signal')
        self.add_output('ArmNodeSocketAction', 'Out')


    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_output', text='Add Arg', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmDynamicSocket'
        op.name_format = "Arg {0}"
        op.index_name_offset = 0
        column = row.column(align=True)
        op = column.operator('arm.node_remove_output', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        if len(self.outputs) == self.min_outputs:
            column.enabled = False
