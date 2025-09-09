from arm.logicnode.arm_nodes import *


class ProbabilisticIndexNode(ArmLogicTreeNode):
    """This system gets an index based on probabilistic values,
    ensuring that the total sum of the probabilities equals 1.
    If the probabilities do not sum to 1, they will be adjusted
    accordingly to guarantee a total sum of 1. Only one output will be
    triggered at a time.

    @output index: the index.

    """

    bl_idname = 'LNProbabilisticIndexNode'
    bl_label = 'Probabilistic Index'
    arm_section = 'logic'
    arm_version = 1

    num_choices: IntProperty(default=0, min=0)

    def __init__(self, *args, **kwargs):
        super(ProbabilisticIndexNode, self).__init__(*args, **kwargs)

    def arm_init(self, context):

        self.add_output('ArmIntSocket', 'Index')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_call_func', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_func'
        op2 = row.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
        op2.callback_name = 'remove_func'

    def add_func(self):
        self.add_input('ArmFloatSocket', f'Prob Index {self.num_choices}')
        self.num_choices += 1

    def remove_func(self):
        if len(self.inputs) > 0:
            self.inputs.remove(self.inputs[-1])
            self.num_choices -= 1

    def draw_label(self) -> str:
        if self.num_choices == 0:
            return self.bl_label

        return f'{self.bl_label}: [{self.num_choices}]'

