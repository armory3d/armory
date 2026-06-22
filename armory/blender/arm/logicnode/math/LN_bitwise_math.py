from arm.logicnode.arm_nodes import *


class BitwiseMathNode(ArmLogicTreeNode):
    """Perform bitwise math on integer values."""
    bl_idname = 'LNBitwiseMathNode'
    bl_label = 'Bitwise Math'
    arm_version = 1

    operators = {
        'negation': '~',
        'and': '&',
        'or': '|',
        'xor': '^',
        'left_shift': '<<',
        'right_shift': '>>',
        'unsigned_right_shift': '>>>'
    }

    def set_mode(self, context):
        if self.property0 == 'negation':
            self.inputs[0].name = 'Operand'
            self.inputs.remove(self.inputs[1])
        else:
            self.inputs[0].name = 'Operand 1'
            if len(self.inputs) < 2:
                self.add_input('ArmIntSocket', 'Operand 2')

    property0: HaxeEnumProperty(
        'property0',
        items=[
            ('negation', 'Negation (~)', 'Performs bitwise negation on the input, so a 0-bit becomes a 1-bit and vice versa'),
            None,
            ('and', 'And (&)', 'A bit in the result is 1 if both bits at the same digit in the operands are 1, else it is 0'),
            ('or', 'Or (|)', 'A bit in the result is 1 if at least one bit at the same digit in the operands is 1, else it is 0'),
            ('xor', 'Xor (^)', 'A bit in the result is 1 if exactly one bit at the same digit in the operands is 1, else it is 0'),
            None,
            ('left_shift', 'Left Shift (<<)', 'Shifts the bits of operand 1 to the left by the amount of operand 2. The result is undefined if operand 2 is negative'),
            ('right_shift', 'Right Shift (>>)', 'Shifts the bits of operand 1 to the right by the amount of operand 2 and keeps the sign of operand 1 (the most significant bit does not change). The result is undefined if operand 2 is negative'),
            ('unsigned_right_shift', 'Unsigned Right Shift (>>>)', 'Shifts the bits of operand 1 to the right by the amount of operand 2, and the most significant bit is set to 0. The result is undefined if operand 2 is negative'),
        ],
        name='Operation',
        description='The operation to perform on the input(s)',
        default='negation',
        update=set_mode
    )

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Operand 1')
        self.add_output('ArmIntSocket', 'Result')

        self.set_mode(context)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0', text='')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.operators[self.property0]}'
