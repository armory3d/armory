from arm.logicnode.arm_nodes import *

class MathNode(ArmLogicTreeNode):
    """Mathematical operations on values."""
    bl_idname = 'LNMathNode'
    bl_label = 'Math'
    arm_version = 3

    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(operation_name):
        return {
            'Add': 0,
            'Subtract': 0,
            'Multiply': 0,
            'Divide': 0,
            'Sine': 1,
            'Cosine': 1,
            'Abs': 1,
            'Tangent': 1,
            'Arcsine': 1,
            'Arccosine': 1,
            'Arctangent': 1,
            'Logarithm': 1,
            'Round': 2,
            'Floor': 1,
            'Ceil': 1,
            'Square Root': 1,
            'Fract': 1,
            'Exponent': 1,
            'Max': 2,
            'Min': 2,
            'Power': 2,
            'Arctan2': 2,
            'Modulo': 2,
            'Less Than': 2,
            'Greater Than': 2,
            'Ping-Pong': 2
        }.get(operation_name, 0)

    def get_enum(self):
        return self.get('property0', 0)

    def set_enum(self, value):
        # Checking the selection of another operation
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0
        if select_prev != select_current:
            # Many arguments: Add, Subtract, Multiply, Divide
            if (self.get_count_in(select_current) == 0):
                while (len(self.inputs) < 2):
                    self.add_input('ArmFloatSocket', 'Value ' + str(len(self.inputs)))
            # 2 arguments: Max, Min, Power, Arctan2, Modulo, Less Than, Greater Than, Ping-Pong
            if (self.get_count_in(select_current) == 2):
                while (len(self.inputs) > 2):
                    self.inputs.remove(self.inputs.values()[-1])
                while (len(self.inputs) < 2):
                    self.add_input('ArmFloatSocket', 'Value ' + str(len(self.inputs)))
            # 1 argument: Sine, Cosine, Abs, Tangent, Arcsine, Arccosine, Arctangent, Logarithm, Round, Floor, Ceil, Square Root, Fract, Exponent
            if (self.get_count_in(select_current) == 1):
                while (len(self.inputs) > 1):
                    self.inputs.remove(self.inputs.values()[-1])
        self['property0'] = value
        if (self.property0 == 'Round'):
            self.inputs[1].name = 'Precision'
        elif (self.property0 == 'Ping-Pong'):
            self.inputs[1].name = 'Scale'
        elif (len(self.inputs) > 1): self.inputs[1].name = 'Value 1'

    property0: HaxeEnumProperty(
        'property0',
        items = [('Add', 'Add', 'Add'),
                 ('Multiply', 'Multiply', 'Multiply'),
                 ('Sine', 'Sine', 'Sine'),
                 ('Cosine', 'Cosine', 'Cosine'),
                 ('Max', 'Maximum', 'Max'),
                 ('Min', 'Minimum', 'Min'),
                 ('Abs', 'Absolute', 'Abs'),
                 ('Subtract', 'Subtract', 'Subtract'),
                 ('Divide', 'Divide', 'Divide'),
                 ('Tangent', 'Tangent', 'Tangent'),
                 ('Arcsine', 'Arcsine', 'Arcsine'),
                 ('Arccosine', 'Arccosine', 'Arccosine'),
                 ('Arctangent', 'Arctangent', 'Arctangent'),
                 ('Power', 'Power', 'Power'),
                 ('Logarithm', 'Logarithm', 'Logarithm'),
                 ('Round', 'Round', 'Round (Value 1 precision of decimal places)'),
                 ('Less Than', 'Less Than', 'Less Than'),
                 ('Greater Than', 'Greater Than', 'Greater Than'),
                 ('Modulo', 'Modulo', 'Modulo'),
                 ('Arctan2', 'Arctan2', 'Arctan2'),
                 ('Floor', 'Floor', 'Floor'),
                 ('Ceil', 'Ceil', 'Ceil'),
                 ('Fract', 'Fract', 'Fract'),
                 ('Square Root', 'Square Root', 'Square Root'),
                 ('Exponent', 'Exponent', 'Exponent'),
                 ('Ping-Pong', 'Ping-Pong', 'The output value is moved between 0.0 and the Scale based on the input value')],
        name='', default='Add', set=set_enum, get=get_enum)

    property1: HaxeBoolProperty('property1', name='Clamp', default=False)

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Value 0', default_value=0.0)
        self.add_input('ArmFloatSocket', 'Value 1', default_value=0.0)

        self.add_output('ArmFloatSocket', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property1')
        layout.prop(self, 'property0')
        # Many arguments: Add, Subtract, Multiply, Divide
        if (self.get_count_in(self.property0) == 0):
            row = layout.row(align=True)
            column = row.column(align=True)
            op = column.operator('arm.node_add_input', text='Add Value', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            op.socket_type = 'ArmFloatSocket'
            op.name_format = 'Value {0}'
            column = row.column(align=True)
            op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op.node_index = str(id(self))
            if len(self.inputs) == 2:
                column.enabled = False

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property0}'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 2):
            raise LookupError()

        return NodeReplacement.Identity(self)
