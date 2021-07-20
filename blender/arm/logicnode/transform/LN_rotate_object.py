from arm.logicnode.arm_nodes import *

class RotateObjectNode(ArmLogicTreeNode):
    """Rotates the given object."""
    bl_idname = 'LNRotateObjectNode'
    bl_label = 'Rotate Object'
    arm_section = 'rotation'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Euler Angles')
        self.add_input('ArmFloatSocket', 'Angle / W')

        self.add_output('ArmNodeSocketAction', 'Out')

    def on_property_update(self, context):
        """ called by the EnumProperty, used to update the node socket labels"""
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
            raise ValueError('No nodesocket labels for current input mode: check self-consistancy of LN_rotate_object.py')

    def draw_buttons(self, context, layout):
        # this block is here to ensure backwards compatibility and warn the user.
        # delete it (only keep the "else" part) when the 'old version' of the node will be considered removed.
        # (note: please also update the corresponding haxe file when doing so)
        if len(self.inputs) < 4:
            row = layout.row(align=True)
            row.label(text="Node has been updated with armory 2020.09. Please consider deleting and recreating it.")
        else:
            layout.prop(self, 'property0')

    property0: HaxeEnumProperty(
        'property0',
        items=[('Euler Angles', 'Euler Angles', 'Euler Angles'),
               ('Angle Axies (Radians)', 'Angle Axies (Radians)', 'Angle Axies (Radians)'),
               ('Angle Axies (Degrees)', 'Angle Axies (Degrees)', 'Angle Axies (Degrees)'),
               ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='Euler Angles',
        update=on_property_update)
