from arm.logicnode.arm_nodes import *

class LookAtNode(ArmLogicTreeNode):
    """Converts the two given coordinates to a quaternion rotation."""
    bl_idname = 'LNLookAtNode'
    bl_label = 'Look At'
    arm_section = 'rotation'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('X', ' X', 'X'),
                 ('-X', '-X', '-X'),
                 ('Y', ' Y', 'Y'),
                 ('-Y', '-Y', '-Y'),
                 ('Z', ' Z', 'Z'),
                 ('-Z', '-Z', '-Z')],
        name='With', default='Z')

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'From Location')
        self.add_input('ArmVectorSocket', 'To Location')

        self.add_output('ArmVectorSocket', 'Rotation')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
