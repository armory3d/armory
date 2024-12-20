from arm.logicnode.arm_nodes import *


class ProbabilisticOutputNode(ArmLogicTreeNode):
    """This system activates an output based on probabilistic values,
    ensuring that the total sum of the probabilities equals 1.
    If the probabilities do not sum to 1, they will be adjusted
    accordingly to guarantee a total sum of 1. Only one output will be
    triggered at a time.

    @input prob: probability of output.
    @output output: output.

    """
    
    bl_idname = 'LNProbabilisticOutputNode'
    bl_label = 'Probabilistic Output'
    arm_section = 'logic'
    arm_version = 1

    num_choices: IntProperty(default=0, min=0)

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):

        self.add_input('ArmNodeSocketAction', 'In')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_call_func', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.callback_name = 'add_func'
        op2 = row.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
        op2.callback_name = 'remove_func'

    def add_func(self):
        self.add_input('ArmFloatSocket', f'Prob {self.num_choices}')
        self.add_output('ArmNodeSocketAction', f'Output {self.num_choices}')
        self.num_choices += 1

    def remove_func(self):
        if len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])
            self.outputs.remove(self.outputs[-1])
            self.num_choices -= 1

    def draw_label(self) -> str:
        if self.num_choices == 0:
            return self.bl_label

        return f'{self.bl_label}: [{self.num_choices}]'

