from arm.logicnode.arm_nodes import *

class MathNode(ArmLogicTreeNode):
    """Mathematical operations on values."""
    bl_idname = 'LNMathNode'
    bl_label = 'Math'
    arm_version = 1
    property0: EnumProperty(
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
                 ('Round', 'Round', 'Round'),
                 ('Less Than', 'Less Than', 'Less Than'),
                 ('Greater Than', 'Greater Than', 'Greater Than'),
                 ('Modulo', 'Modulo', 'Modulo'),
                 ('Arctan2', 'Arctan2', 'Arctan2'),
                 ('Floor', 'Floor', 'Floor'),
                 ('Ceil', 'Ceil', 'Ceil'),
                 ('Fract', 'Fract', 'Fract'),
                 ('Square Root', 'Square Root', 'Square Root'),
                 ('Exp', 'Exponent', 'Exponent'),
                 ],
        name='', default='Add')

    @property
    def property1(self):
        return 'true' if self.property1_ else 'false'

    property1_: BoolProperty(name='Clamp', default=False)

    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(MathNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Value 0', default_value=0.0)
        self.add_input('NodeSocketFloat', 'Value 1', default_value=0.0)
        self.add_output('NodeSocketFloat', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property1_')
        layout.prop(self, 'property0')
        # Add, Subtract, Multiply, Divide
        if (self.property0 == "Add") or (self.property0 == "Subtract") or (self.property0 == "Multiply") or (self.property0 == "Divide"):
            while (len(self.inputs) < 2):
                self.add_input('NodeSocketFloat', 'Value ' + str(len(self.inputs)))
            row = layout.row(align=True)
            column = row.column(align=True)
            op = column.operator('arm.node_add_input', text='Add Value', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            op.socket_type = 'NodeSocketFloat'
            op.name_format = 'Value {0}'
            column = row.column(align=True)
            op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op.node_index = str(id(self))
            if len(self.inputs) == 2:
                column.enabled = False
        # Max, Min, Power, Arctan2, Modulo, Less Than, Greater Than
        if (self.property0 == "Max") or (self.property0 == "Min") or (self.property0 == "Power") or (self.property0 == "Arctan2") or (self.property0 == "Modulo") or (self.property0 == "Less Than") or (self.property0 == "Greater Than"):
            while (len(self.inputs) > 2):
                self.inputs.remove(self.inputs.values()[-1])
            while (len(self.inputs) < 2):
                self.add_input('NodeSocketFloat', 'Value ' + str(len(self.inputs)))
        # Sine, Cosine, Abs, Tangent, Arcsine, Arccosine, Arctangent, Logarithm, Round, Floor, Ceil, Square Root, Fract, Exponent
        if (self.property0 == "Sine") or (self.property0 == "Cosine") or (self.property0 == "Abs") or (self.property0 == "Tangent") or (self.property0 == "Arcsine") or (self.property0 == "Arccosine") or (self.property0 == "Arctangent") or (self.property0 == "Logarithm") or (self.property0 == "Round") or (self.property0 == "Floor") or (self.property0 == "Ceil") or (self.property0 == "Square Root") or (self.property0 == "Fract") or (self.property0 == "Exp"):
            while (len(self.inputs) > 1):
                self.inputs.remove(self.inputs.values()[-1])