from arm.logicnode.arm_nodes import *

class OnGamepadNode(ArmLogicTreeNode):
    """On gamepad node"""
    bl_idname = 'LNOnGamepadNode'
    bl_label = 'On Gamepad'
    arm_version = 1

    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
                 # ('Moved Left', 'Moved Left', 'Moved Left'),
                 # ('Moved Right', 'Moved Right', 'Moved Right'),],
        name='', default='Started')

    property1: EnumProperty(
        items = [('cross', 'cross / a', 'cross / a'),
                 ('circle', 'circle / b', 'circle / b'),
                 ('square', 'square / x', 'square / x'),
                 ('triangle', 'triangle / y', 'triangle / y'),
                 ('l1', 'l1', 'l1'),
                 ('r1', 'r1', 'r1'),
                 ('l2', 'l2', 'l2'),
                 ('r2', 'r2', 'r2'),
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

    def init(self, context):
        super(OnGamepadNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_input('NodeSocketInt', 'Gamepad')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(OnGamepadNode, category=PKG_AS_CATEGORY, section='gamepad')
