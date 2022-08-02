from arm.logicnode.arm_nodes import *


class RotationNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """A rotation, created from one of its possible mathematical representations"""
    bl_idname = 'LNRotationNode'
    bl_label = 'Rotation'
    bl_description = 'Create a Rotation object, describing the difference between two orientations (internally represented as a quaternion for efficiency)'
    #arm_section = 'rotation'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Euler Angles / Vector XYZ')
        self.add_input('ArmFloatSocket', 'Angle / W')

        self.add_output('ArmRotationSocket', 'Out', is_var=True)

    def on_property_update(self, context):
        """called by the EnumProperty, used to update the node socket labels"""
        if self.property0 == "Quaternion":
            self.inputs[0].name = "Quaternion XYZ"
            self.inputs[1].name = "Quaternion W"
        elif self.property0 == "EulerAngles":
            self.inputs[0].name = "Euler Angles"
            self.inputs[1].name = "[unused for Euler input]"
        elif self.property0 == "AxisAngle":
            self.inputs[0].name = "Axis"
            self.inputs[1].name = "Angle"
        else:
            raise ValueError('No nodesocket labels for current input mode: check self-consistancy of LN_rotation.py')

    def draw_content(self, context, layout):
        coll = layout.column(align=True)
        coll.prop(self, 'property0')
        if self.property0 in ('EulerAngles','AxisAngle'):
            coll.prop(self, 'property1')
            if self.property0=='EulerAngles':
                coll.prop(self, 'property2')

    property0: HaxeEnumProperty(
        'property0',
        items = [('EulerAngles', 'Euler Angles', 'Euler Angles'),
                 ('AxisAngle', 'Axis/Angle', 'Axis/Angle'),
                 ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='EulerAngles',
        update=on_property_update)

    property1: HaxeEnumProperty(
        'property1',
        items=[('Deg', 'Degrees', 'Degrees'),
               ('Rad', 'Radians', 'Radians')],
        name='', default='Rad')
    property2: HaxeEnumProperty(
        'property2',
        items=[('XYZ','XYZ','XYZ'),
               ('XZY','XZY (legacy Armory euler order)','XZY (legacy Armory euler order)'),
               ('YXZ','YXZ','YXZ'),
               ('YZX','YZX','YZX'),
               ('ZXY','ZXY','ZXY'),
               ('ZYX','ZYX','ZYX')],
        name='', default='XYZ'
    )

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.property0 = master_node.property0
        self.property1 = master_node.property1
        self.property2 = master_node.property2

        for i in range(len(self.inputs)):
            self.inputs[i].default_value_raw = master_node.inputs[i].get_default_value()
