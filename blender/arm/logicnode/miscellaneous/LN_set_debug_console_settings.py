from arm.logicnode.arm_nodes import *

class SetDebugConsoleSettings(ArmLogicTreeNode):
    """Sets the debug console settings."""
    bl_idname = 'LNSetDebugConsoleSettings'
    bl_label = 'Set Debug Console Settings'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('left', 'Anchor Left', 'Anchor debug console in the top left'),
                 ('center', 'Anchor Center', 'Anchor debug console in the top center'),
                 ('right', 'Anchor Right', 'Anchor the debug console in the top right')],
        name='', default='right')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Visible')
        self.add_input('ArmFloatSocket', 'Scale', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
