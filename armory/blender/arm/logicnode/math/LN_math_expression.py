from arm.logicnode.arm_nodes import *
import re

class MathExpressionNode(ArmLogicTreeNode):
    """Mathematical operations on values."""
    bl_idname = 'LNMathExpressionNode'
    bl_label = 'Math Expression'
    arm_version = 2

    num_params: IntProperty(default=2, min=0)

    @staticmethod
    def get_variable_name(index):
        return chr( range(ord('a'), ord('z')+1)[index] )

    def set_exp(self, value):
        self['property2'] = value
        # TODO: Check expression for errors
        self['exp_error'] = False

    def get_exp(self):
        return self.get('property2', 'a + b')

    property0: HaxeBoolProperty('property0', name='Clamp Result', default=False)
    property1: HaxeIntProperty('property1', name='Number of Params', default=2)
    property2: HaxeStringProperty('property2', name='', description='Math Expression: +, -, *, /, ^, %, (, ), log(a, b), ln(a), abs(a), max(a,b), min(a,b), sin(a), cos(a), tan(a), cot(a), asin(a), acos(a), atan(a), atan2(a,b), pi(), e()', set=set_exp, get=get_exp)

    def __init__(self, *args, **kwargs):
        super(MathExpressionNode, self).__init__(*args, **kwargs)
        self.register_id()


    def arm_init(self, context):

        # OUTPUTS:
        self.add_output('ArmFloatSocket', 'Result')

        # two default parameters at start
        self.add_input('ArmFloatSocket', self.get_variable_name(0), default_value=0.0)
        self.add_input('ArmFloatSocket', self.get_variable_name(1), default_value=0.0)

    def add_sockets(self):
        if self.num_params < 26:
            self.add_input('ArmFloatSocket', self.get_variable_name(self.num_params), default_value=0.0)
            self.num_params += 1
            self['property1'] = self.num_params

    def remove_sockets(self):
        if self.num_params > 0:
            self.inputs.remove(self.inputs.values()[-1])
            self.num_params -= 1
            self['property1'] = self.num_params

    def draw_buttons(self, context, layout):
        # Clamp Property
        layout.prop(self, 'property0')

        # Expression Property
        row = layout.row(align=True)
        column = row.column(align=True)
        # TODO:
        #column.alert = self['exp_error']
        column.prop(self, 'property2', icon='FORCE_HARMONIC')

        # Button ADD parameter
        row = layout.row(align=True)
        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='Add Param', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.callback_name = 'add_sockets'
        if self.num_params == 26:
            column.enabled = False

        # Button REMOVE parameter
        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        op.callback_name = 'remove_sockets'
        if self.num_params == 0:
            column.enabled = False
