from arm.logicnode.arm_nodes import *

class GamepadSticksNode(ArmLogicTreeNode):
    """Activates the output on the given gamepad event.

    @seeNode Gamepad Coords

    @input Gamepad: the ID of the gamepad.

    @option state: the state of the gamepad stick to listen to.
    @option stick: the gamepad stick that should activate the output.
    @option axis: the gamepad stick axis value
    """
    bl_idname = 'LNGamepadSticksNode'
    bl_label = 'Gamepad Sticks'
    arm_version = 1
    arm_section = 'gamepad'

    property0: HaxeEnumProperty(
        'property0',
        items = [('Started', 'Started', 'Started'),
                 ('Down', 'Down', 'Down'),
                 ('Released', 'Released', 'Released'),],
        name='', default='Down')

    property1: HaxeEnumProperty(
        'property1',
        items = [('LeftStick', 'LeftStick', 'LeftStick'), ('RightStick', 'RightStick', 'RightStick'),],
        name='', default='LeftStick')

    property2: HaxeEnumProperty(
        'property2',
        items = [('up', 'up', 'up'),
                 ('down', 'down', 'down'),
                 ('left', 'left', 'left'),
                 ('right', 'right', 'right'),
                 ('up-left', 'up-left', 'up-left'),
                 ('up-right', 'up-right', 'up-right'),
                 ('down-left', 'down-left', 'down-left'),
                 ('down-right', 'down-right', 'down-right'),],
        name='', default='up')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

        self.add_input('ArmIntSocket', 'Gamepad')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
        layout.prop(self, 'property2')