from arm.logicnode.arm_nodes import *

class StringMapNode(ArmLogicTreeNode):
    """Create String Map

    @input In: Create a map using given keys and values.

    @input Key: Key.

    @input Value: Value.

    @output Out: Run after map is created.

    @output Map: The created map.
    """

    bl_idname = 'LNStringMapNode'
    bl_label = 'String Map'
    arm_version = 1

    min_inputs = 1
    property0: HaxeIntProperty('property0', name='Number of keys', default=0)

    def __init__(self):
        super(StringMapNode, self).__init__()
        self.register_id()

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Map')

    def add_sockets(self):
        self.add_input('ArmStringSocket', f'Key [{self.property0}]')
        self.add_input('ArmStringSocket', f'Value [{self.property0}]')
        self.property0 += 1

    def remove_sockets(self):
        if self.property0 > 0:
            self.inputs.remove(self.inputs.values()[-1])
            self.inputs.remove(self.inputs.values()[-1])
            self.property0 -= 1

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_call_func', text='New', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.callback_name = 'add_sockets'
        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        op.callback_name = 'remove_sockets'
        if len(self.inputs) == self.min_inputs:
            column.enabled = False
