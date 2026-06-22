from arm.logicnode.arm_nodes import *


class EmitSignalNode(ArmLogicTreeNode):
    """Emits a Signal with optional arguments.

    Connect a Signal instance to the Signal input. When this node is activated,
    it calls emit() on the Signal, passing any connected arguments to all
    connected OnSignal nodes.

    Use 'Add Arg' to add input sockets for passing data to listeners.

    @seeNode Signal
    @seeNode On Signal"""

    bl_idname = 'LNEmitSignalNode'
    bl_label = 'Emit Signal'
    arm_version = 1
    arm_section = 'signal'
    min_inputs = 2


    def __init__(self, *args, **kwargs):
        super(EmitSignalNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Signal')
        self.add_output('ArmNodeSocketAction', 'Out')


    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='Add Arg', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmDynamicSocket'
        op.name_format = "Arg {0}"
        op.index_name_offset = -1
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        if len(self.inputs) == self.min_inputs:
            column.enabled = False
