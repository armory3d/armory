from arm.logicnode.arm_nodes import *
import re

class MathExpressionNode(ArmLogicTreeNode):
    """Mathematical operations on values."""
    bl_idname = 'LNMathExpressionNode'
    bl_label = 'Math Expression'
    arm_version = 1
    min_inputs = 2
    max_inputs = 10

    @staticmethod
    def get_variable_name(index):
        return {
            0: 'a',
            1: 'b',
            2: 'c',
            3: 'd',
            4: 'e',
            5: 'x',
            6: 'y',
            7: 'h',
            8: 'i',
            9: 'k'
        }.get(index, 'a')

    @staticmethod
    def get_clear_exp(value):
        return re.sub(r'[\-\+\*\/\(\)\^\%abcdexyhik0123456789. ]', '', value).strip()

    @staticmethod
    def get_invalid_characters(value):
        value = value.replace(' ', '')
        len_v = len(value)
        arg = ['a', 'b', 'c', 'd', 'e', 'x', 'y', 'h', 'i', 'k']
        for i in range(len_v):
            s = value[i]
            if s == '.':
                if ((i - 1) < 0) or ((i + 1) >= len_v) or (not value[i - 1].isnumeric()) or (not value[i + 1].isnumeric()):
                    return False
            oper = ['+', '-', '*', '/', '%', '^']
            if s == '(':
                if (i > 0) and ((value[i - 1] not in oper) and (value[i - 1] != '(')):
                    return False
                if (i < (len_v - 1)) and ((value[i + 1] not in arg) and (not value[i + 1].isnumeric()) and (value[i + 1] != '(')):
                    return False
            if s == ')':
                if (i > 0) and ((value[i - 1] not in arg) and (not value[i - 1].isnumeric()) and (value[i - 1] != ')')):
                    return False
                if (i < (len_v - 1)) and (not value[i + 1].isnumeric()) and ((value[i + 1] not in oper) and (value[i + 1] != ')')):
                    return False
            if s in oper:
                if ((i > 0) and (value[i - 1] in oper)) or ((i < (len_v - 1)) and (value[i + 1] in oper)):
                    return False
        last_sym = value[len_v - 1]
        if (not last_sym.isnumeric()) and (last_sym not in arg) and (last_sym != ')'):
            return False
        return True

    @staticmethod
    def check_variable(self, value):
        variables = re.sub(r'[\-\+\*\/\(\)\^\%0123456789. ]', '', value).strip()
        for vr in variables:
            check = False
            for inp_key in self.inputs.keys():
                if (vr == inp_key):
                    check = True
                    break
            if not check:
                return False
        return True

    @staticmethod
    def matches(line, opendelim='(', closedelim=')'):
        stack = []
        for m in re.finditer(r'[{}{}]'.format(opendelim, closedelim), line):
            pos = m.start()
            if line[pos-1] == '\\':
                # Skip escape sequence
                continue
            c = line[pos]
            if c == opendelim:
                stack.append(pos+1)
            elif c == closedelim:
                if len(stack) > 0:
                    prevpos = stack.pop()
                    yield (True, prevpos, pos, len(stack))
                else:
                    # Error
                    yield (False, 0, 0, 0)
                    pass
        if len(stack) > 0:
            for pos in stack:
                yield (False, 0, 0, 0)

    @staticmethod
    def isPartCorrect(s):
        if len(s.replace('p', '').replace(' ', '').split()) == 0:
            return True
        REGEX = re.compile(r"(([abcdexyhikp]|\d+)[\+\-\/\*\^\%]){1,}([abcdexyhikp]|\d+)(=([abcdexyhikp]|\d+))?")
        result = False
        if REGEX.match(s):
            result = True
        return result

    @staticmethod
    def isCorrect(self, s):
        result = True
        if s.find("(") >=0 or s.find(")") >= 0:
            for correct, openpos, closepos, level in self.matches(s):
                if correct:
                    part = s[openpos:closepos]
                    if part.find("(") == -1 and part.find(")") == -1:
                        if not self.isPartCorrect(part):
                            result = False
                            break
                    part = s[openpos-1:closepos+1]
                    replaced = s.replace(part, "p")
                    if replaced.find("(") >=0 or replaced.find(")") >= 0:
                        if not self.isCorrect(self, replaced):
                            result = False
                            break
                    else:
                        if not self.isPartCorrect(replaced):
                            result = False
                            break
                else:
                    result = False
                    break
        else:
            result = self.isPartCorrect(s)
        return result

    def set_exp_error(self, value):
        self['exp_error'] = value

    def get_exp_error(self):
        return self.get('exp_error', False)

    def set_exp(self, value):
        value = value.lower()
        self['property0'] = value
        # Check errors
        val_error = False
        if len(self.get_clear_exp(value)) > 0:
            val_error = True
        elif not self.get_invalid_characters(value):
            val_error = True
        elif not self.check_variable(self, value):
            val_error = True
        elif not self.isCorrect(self, value.replace(' ', '')):
            val_error = True
        self.set_exp_error(val_error)

    def get_exp(self):
        return self.get('property0', 'a + b')

    property0: HaxeStringProperty('property0', name='', description='Expression (operation: +, -, *, /, ^, (, ), %)', set=set_exp, get=get_exp)
    property1: HaxeBoolProperty('property1', name='Clamp', default=False)

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', self.get_variable_name(0), default_value=0.0)
        self.add_input('ArmFloatSocket', self.get_variable_name(1), default_value=0.0)
        self.add_output('ArmFloatSocket', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property1')
        # Expression
        row = layout.row(align=True)
        column = row.column(align=True)
        column.alert = self.get_exp_error()
        column.prop(self, 'property0', icon='FORCE_HARMONIC')
        # Buttons
        row = layout.row(align=True)
        column = row.column(align=True)
        op = column.operator('arm.node_add_input', text='Add Value', icon='PLUS', emboss=True)
        if len(self.inputs) == 10:
            column.enabled = False
        op.node_index = str(id(self))
        op.socket_type = 'ArmFloatSocket'
        op.name_format = self.get_variable_name(len(self.inputs))
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        if len(self.inputs) == 2:
            column.enabled = False
