from arm.logicnode.arm_nodes import *

class SetRotationNode(ArmLogicTreeNode):
    """Sets the rotation of the given object."""
    bl_idname = 'LNSetRotationNode'
    bl_label = 'Set Object Rotation'
    arm_section = 'rotation'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Euler Angles / Vector XYZ')
        self.add_input('ArmFloatSocket', 'Angle / W')

        self.add_output('ArmNodeSocketAction', 'Out')

    def on_property_update(self, context):
        """called by the EnumProperty, used to update the node socket labels"""
        if self.property0 == "Quaternion":
            self.inputs[2].name = "Quaternion XYZ"
            self.inputs[3].name = "Quaternion W"
        elif self.property0 == "Euler Angles":
            self.inputs[2].name = "Euler Angles"
            self.inputs[3].name = "[unused for Euler input]"
        elif self.property0.startswith("Angle Axies"):
            self.inputs[2].name = "Axis"
            self.inputs[3].name = "Angle"
        else:
            raise ValueError('No nodesocket labels for current input mode: check self-consistancy of action_set_rotation.py')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    property0: HaxeEnumProperty(
        'property0',
        items = [('Euler Angles', 'Euler Angles', 'Euler Angles'),
                 ('Angle Axies (Radians)', 'Angle Axies (Radians)', 'Angle Axies (Radians)'),
                 ('Angle Axies (Degrees)', 'Angle Axies (Degrees)', 'Angle Axies (Degrees)'),
                 ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='Euler Angles',
        update=on_property_update)
