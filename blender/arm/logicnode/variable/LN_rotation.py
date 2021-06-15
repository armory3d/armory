from arm.logicnode.arm_nodes import *

class RotationNode(ArmLogicTreeNode):
    """A rotation, created from one of its possible mathematical representations"""
    bl_idname = 'LNRotationNode'
    bl_label = 'Rotation'
    #arm_section = 'rotation'
    arm_version = 1

    def init(self, context):
        super(RotationNode, self).init(context)
        self.add_input('NodeSocketVector', 'Euler Angles / Vector XYZ')
        self.add_input('NodeSocketFloat', 'Angle / W')
        
        self.add_output('ArmNodeSocketRotation', 'Out', is_var=True)

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

    def draw_buttons(self, context, layout):
        coll = layout.column(align=True)
        coll.prop(self, 'property0')
        if self.property0 in ('EulerAngles','AxisAngle'):
            coll.prop(self, 'property1')
            if self.property0=='EulerAngles':
                coll.prop(self, 'property2')

    property0: EnumProperty(
        items = [('EulerAngles', 'Euler Angles', 'Euler Angles'),
                 ('AxisAngle', 'Axis/Angle', 'Axis/Angle'),
                 ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='EulerAngles',
        update=on_property_update)

    property1: EnumProperty(
        items=[('Deg', 'Degrees', 'Degrees'),
               ('Rad', 'Radians', 'Radians')],
        name='', default='Rad')
    property2: EnumProperty(
        items=[('XYZ','XYZ','XYZ'),
               ('XZY','XZY (legacy Armory euler order)','XZY (legacy Armory euler order)'),
               ('YXZ','YXZ','YXZ'),
               ('YZX','YZX','YZX'),
               ('ZXY','ZXY','ZXY'),
               ('ZYX','ZYX','ZYX')],
        name='', default='XYZ'
    )
