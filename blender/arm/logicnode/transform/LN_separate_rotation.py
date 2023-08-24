from arm.logicnode.arm_nodes import *

class SeparateRotationNode(ArmLogicTreeNode):
    """Decompose a rotation into one of its mathematical representations"""
    bl_idname = 'LNSeparateRotationNode'
    bl_label = 'Separate Rotation'
    arm_section = 'rotation'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmRotationSocket', 'Angle')

        self.add_output('ArmVectorSocket', 'Euler Angles / Vector XYZ')
        self.add_output('ArmFloatSocket', 'Angle / W')
        

    def on_property_update(self, context):
        """called by the EnumProperty, used to update the node socket labels"""
        if self.property0 == 'Quaternion':
            self.outputs[0].name = "Quaternion XYZ"
            self.outputs[1].name = "Quaternion W"
        elif self.property0 == 'EulerAngles':
            self.outputs[0].name = "Euler Angles"
            self.outputs[1].name = "[unused for Euler output]"
        elif self.property0 == 'AxisAngle':
            self.outputs[0].name = "Axis"
            self.outputs[1].name = "Angle"
        else:
            raise ValueError('No nodesocket labels for current input mode: check self-consistancy of LN_separate_rotation.py')

    def draw_buttons(self, context, layout):
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
        name='', default='XYZ')
