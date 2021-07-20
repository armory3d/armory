from arm.logicnode.arm_nodes import *

class QuaternionMathNode(ArmLogicTreeNode):
    """Mathematical operations on quaternions."""
    bl_idname = 'LNQuaternionMathNode'
    bl_label = 'Quaternion Math'
    arm_section = 'quaternions'
    arm_version = 1

    def get_bool(self):
        return self.get('property1', False)

    def set_bool(self, value):
        self['property1'] = value
        if value:
            if ((self.property0 == 'Module') or (self.property0 == 'DotProduct') or (self.property0 == 'ToAxisAngle')) and (len(self.outputs) > 1):
                self.outputs.remove(self.outputs.values()[-1]) # Module/DotProduct/ToAxisAngle
            self.add_output('ArmFloatSocket', 'X') # Result X
            self.add_output('ArmFloatSocket', 'Y') # Result Y
            self.add_output('ArmFloatSocket', 'Z') # Result Z
            self.add_output('ArmFloatSocket', 'W') # Result W
            if (self.property0 == 'Module'):
                self.add_output('ArmFloatSocket', 'Module') # Module
            if (self.property0 == 'DotProduct'):
                self.add_output('ArmFloatSocket', 'Scalar') # DotProduct
            if (self.property0 == 'ToAxisAngle'):
                self.add_output('ArmFloatSocket', 'To Axis Angle') # ToAxisAngle
        else:
            if ((self.property0 == 'Module') or (self.property0 == 'DotProduct') or (self.property0 == 'ToAxisAngle')) and (len(self.outputs) > 1):
                self.outputs.remove(self.outputs.values()[-1]) # Module/DotProduct/ToAxisAngle
            # Remove X, Y, Z, W
            for i in range(4):
                if len(self.outputs) > 1:
                    self.outputs.remove(self.outputs.values()[-1])
                else:
                    break
            if (self.property0 == 'Module'):
                self.add_output('ArmFloatSocket', 'Module') # Module
            if (self.property0 == 'DotProduct'):
                self.add_output('ArmFloatSocket', 'Scalar') # DotProduct
            if (self.property0 == 'ToAxisAngle'):
                self.add_output('ArmFloatSocket', 'To Axis Angle') # ToAxisAngle

    property1: HaxeBoolProperty('property1', name='Separator Out', default=False, set=set_bool, get=get_bool)

    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(operation_name):
        return {
            'Add': 0,
            'Subtract': 0,
            'DotProduct': 0,
            'Multiply': 0,
            'MultiplyFloats': 0,
            'Module': 1,
            'Normalize': 1,
            'GetEuler': 1,
            'FromTo': 2,
            'FromMat': 2,
            'FromRotationMat': 2,
            'ToAxisAngle': 2,
            'Lerp': 3,
            'Slerp': 3,
            'FromAxisAngle': 3,
            'FromEuler': 3
        }.get(operation_name, 0)

    def get_enum(self):
        return self.get('property0', 0)

    def set_enum(self, value):
        # Checking the selection of another operation
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0
        if select_prev != select_current:
            # Remove
            count = 0
            if ((select_prev == 'Add') or (select_prev == 'Subtract') or (select_prev == 'Multiply') or (select_prev == 'DotProduct')) and ((select_current == 'Add') or (select_current == 'Subtract') or (select_current == 'Multiply') or (select_current == 'DotProduct')) or (((select_current == 'Lerp') or (select_current == 'Slerp')) and ((select_prev == 'Lerp') or (select_prev == 'Slerp'))):
                count = len(self.inputs)
            while (len(self.inputs) > count):
                self.inputs.remove(self.inputs.values()[-1])
            if (select_prev == 'DotProduct') or (select_prev == 'ToAxisAngle') or (select_prev == 'Module'):
                self.outputs.remove(self.outputs.values()[-1])

            # Many arguments: Add, Subtract, DotProduct, Multiply, MultiplyFloat
            if (self.get_count_in(select_current) == 0):
                if (select_current == "MultiplyFloats"):
                    self.add_input('ArmVectorSocket', 'Quaternion ' + str(len(self.inputs)))
                    self.add_input('ArmFloatSocket', 'Value ' + str(len(self.inputs)))
                else:
                    while (len(self.inputs) < 2):
                        self.add_input('ArmVectorSocket', 'Quaternion ' + str(len(self.inputs)))
                if (select_current == 'DotProduct'):
                    self.add_output('ArmFloatSocket', 'Scalar')

            # 3 arguments: Lerp, Slerp, FromAxisAngle, FromEuler
            if (self.get_count_in(select_current) == 3):
                if (select_current == 'Lerp') or (select_current == 'Slerp'):
                    while (len(self.inputs) < 3):
                        self.add_input('ArmVectorSocket', 'From')
                        self.add_input('ArmVectorSocket', 'To')
                        self.add_input('ArmFloatSocket', 'T')
                if (select_current == 'FromAxisAngle'):
                    self.add_input('ArmVectorSocket', 'Quaternion')
                    self.add_input('ArmVectorSocket', 'Axis')
                    self.add_input('ArmFloatSocket', 'Angle')
                if (select_current == 'FromEuler'):
                    self.add_input('ArmFloatSocket', 'X')
                    self.add_input('ArmFloatSocket', 'Y')
                    self.add_input('ArmFloatSocket', 'Z')

            # 2 arguments: FromTo, FromMat, FromRotationMat, ToAxisAngle
            if (self.get_count_in(select_current) == 2):
                if (select_current == 'FromTo'):
                    self.add_input('ArmVectorSocket', 'Vector ' + str(len(self.inputs)))
                    self.add_input('ArmVectorSocket', 'Vector ' + str(len(self.inputs)))
                if (select_current == 'FromMat') or (select_current == 'FromRotationMat'):
                    self.add_input('ArmVectorSocket', 'Quaternion')
                    self.add_input('ArmDynamicSocket', 'Matrix')
                if (select_current == 'ToAxisAngle'):
                    self.add_input('ArmVectorSocket', 'Quaternion')
                    self.add_input('ArmVectorSocket', 'Axis')
                    self.add_output('ArmFloatSocket', 'Angle')

            # 1 argument: Module, Normalize, GetEuler
            if (self.get_count_in(select_current) == 1):
                self.add_input('ArmVectorSocket', 'Quaternion')
                if (select_current == 'Module'):
                    self.add_output('ArmFloatSocket', 'Module')
        self['property0'] = value

    property0: HaxeEnumProperty(
        'property0',
        items = [('Add', 'Add', 'Add'),
                 ('Subtract', 'Subtract', 'Subtract'),
                 ('DotProduct', 'Dot Product', 'Dot Product'),
                 ('Multiply', 'Multiply', 'Multiply'),
                 ('MultiplyFloats', 'Multiply (Floats)', 'Multiply (Floats)'),
                 ('Module', 'Module', 'Module'),
                 ('Normalize', 'Normalize', 'Normalize'),
                 ('Lerp', 'Lerp', 'Linearly interpolate'),
                 ('Slerp', 'Slerp', 'Spherical linear interpolation'),
                 ('FromTo', 'From To', 'From To'),
                 ('FromMat', 'From Mat', 'From Mat'),
                 ('FromRotationMat', 'From Rotation Mat', 'From Rotation Mat'),
                 ('ToAxisAngle', 'To Axis Angle', 'To Axis Angle'),
                 ('FromAxisAngle', 'From Axis Angle', 'From Axis Angle'),
                 ('FromEuler', 'From Euler', 'From Euler'),
                 ('GetEuler', 'To Euler', 'To Euler')],
        name='', default='Add', set=set_enum, get=get_enum)

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Quaternion 0', default_value=[0.0, 0.0, 0.0])
        self.add_input('ArmVectorSocket', 'Quaternion 1', default_value=[0.0, 0.0, 0.0])
        self.add_output('ArmVectorSocket', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property1') # Separator Out
        layout.prop(self, 'property0') # Operation
        # Buttons
        if (self.get_count_in(self.property0) == 0):
            row = layout.row(align=True)
            column = row.column(align=True)
            op = column.operator('arm.node_add_input', text='Add Value', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            if (self.property0 == 'Add') or (self.property0 == 'Subtract') or (self.property0 == 'Multiply') or (self.property0 == 'DotProduct'):
                op.name_format = 'Quaternion {0}'
            else:
                op.name_format = 'Value {0}'
            if (self.property0 == "MultiplyFloats"):
                op.socket_type = 'ArmFloatSocket'
            else:
                op.socket_type = 'ArmVectorSocket'
            column = row.column(align=True)
            op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op.node_index = str(id(self))
            if len(self.inputs) == 2:
                column.enabled = False
