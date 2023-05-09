from arm.logicnode.arm_nodes import *


class CaseIndexNode(ArmLogicTreeNode):
    """Compare the given `Compare` value with the other inputs for equality
    and return the index of the first match. This is particularly helpful
    in combination with the `Select` node.

    @seeNode Select

    @input Compare: the value to be compared
    @input Value: values for the dynamic comparison

    @output Index: the index of the first equal value, or `null` if no
        equal value was found.
    """
    bl_idname = 'LNCaseIndexNode'
    bl_label = 'Case Index'
    arm_version = 1
    min_inputs = 2

    num_choices: IntProperty(default=0, min=0)

    def __init__(self):
        super().__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Compare')
        self.add_input_func()

        self.add_output('ArmIntSocket', 'Index')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_call_func', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_input_func'

        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'remove_input_func'
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def add_input_func(self):
        self.add_input('ArmDynamicSocket', f'Value {self.num_choices}')
        self.num_choices += 1

    def remove_input_func(self):
        if len(self.inputs) > self.min_inputs:
            self.inputs.remove(self.inputs[-1])
            self.num_choices -= 1

    def draw_label(self) -> str:
        if self.num_choices == 0:
            return self.bl_label

        return f'{self.bl_label}: [{self.num_choices}]'
