from arm.logicnode.arm_nodes import *

class GamepadNode(ArmLogicTreeNode):
    """Activates the output on the given gamepad event.

    @seeNode Gamepad Coords

    @input Gamepad: the ID of the gamepad.

    @option State: the state of the gamepad button to listen to.
    @option Button: the gamepad button that should activate the output.
    """
    bl_idname = 'LNMergedGamepadNode'
    bl_label = 'Gamepad'
    arm_version = 1
    arm_section = 'gamepad'

    property0: HaxeEnumProperty(
        'property0',
        items = [('started', 'Started', 'The gamepad button starts to be pressed'),
                 ('down', 'Down', 'The gamepad button is pressed'),
                 ('released', 'Released', 'The gamepad button stops being pressed')],
                 # ('Moved Left', 'Moved Left', 'Moved Left'),
                 # ('Moved Right', 'Moved Right', 'Moved Right'),],
        name='', default='down')

    property1: HaxeEnumProperty(
        'property1',
        items = [('cross', 'cross / a', 'cross / a'),
                 ('circle', 'circle / b', 'circle / b'),
                 ('square', 'square / x', 'square / x'),
                 ('triangle', 'triangle / y', 'triangle / y'),
                 ('l1', 'l1 / lb', 'l1 / lb'),
                 ('r1', 'r1 / rb', 'r1 / rb'),
                 ('l2', 'l2 / lt', 'l2 / lt'),
                 ('r2', 'r2 / rt', 'r2 / rt'),
                 ('share', 'share', 'share'),
                 ('options', 'options', 'options'),
                 ('l3', 'l3', 'l3'),
                 ('r3', 'r3', 'r3'),
                 ('up', 'up', 'up'),
                 ('down', 'down', 'down'),
                 ('left', 'left', 'left'),
                 ('right', 'right', 'right'),
                 ('home', 'home', 'home'),
                 ('touchpad', 'touchpad', 'touchpad'),],
        name='', default='cross')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

        self.add_input('ArmIntSocket', 'Gamepad')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

    def draw_label(self) -> str:
        inp_gamepad = self.inputs['Gamepad']
        if inp_gamepad.is_linked:
            return f'{self.bl_label}: {self.property1}'

        return f'{self.bl_label} {inp_gamepad.default_value_raw}: {self.property1}'
