from arm.logicnode.arm_nodes import *


class TweenFloatNode(ArmLogicTreeNode):
    """Tween a float value.

    @input Start: Start tweening
    @input Stop: Stop a tweening. tweening can be re-started via the `Start`input
    @input From: Tween start value
    @input To: Tween final value
    @input Duration: Duartion of the tween in seconds

    @output Out: Executed immidiately after `Start` or `Stop` is called
    @output Tick: Executed at every time step in the tween duration
    @output Done: Executed when tween is successfully completed. Not executed if tweening is stopped mid-way
    @output Value: Current tween value
    """
    bl_idname = 'LNTweenFloatNode'
    bl_label = 'Tween Float'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('Linear', 'Linear', 'Linear'),
                ('SineIn', 'SineIn', 'SineIn'),
                ('SineOut', 'SineOut', 'SineOut'),
                ('SineInOut', 'SineInOut', 'SineInOut'),
                ('QuadIn', 'QuadIn', 'QuadIn'),
                ('QuadOut', 'QuadOut', 'QuadOut'),
                ('QuadInOut', 'QuadInOut', 'QuadInOut'),
                ('CubicIn', 'CubicIn', 'CubicIn'),
                ('CubicOut', 'CubicOut', 'CubicOut'),
                ('CubicInOut', 'CubicInOut', 'CubicInOut'),
                ('QuartIn', 'QuartIn', 'QuartIn'),
                ('QuartOut', 'QuartOut', 'QuartOut'),
                ('QuartInOut', 'QuartInOut', 'QuartInOut'),
                ('QuintIn', 'QuintIn', 'QuintIn'),
                ('QuintOut', 'QuintOut', 'QuintOut'),
                ('QuintInOut', 'QuintInOut', 'QuintInOut'),
                ('ExpoIn', 'ExpoIn', 'ExpoIn'),
                ('ExpoOut', 'ExpoOut', 'ExpoOut'),
                ('ExpoInOut', 'ExpoInOut', 'ExpoInOut'),
                ('CircIn', 'CircIn', 'CircIn'),
                ('CircOut', 'CircOut', 'CircOut'),
                ('CircInOut', 'CircInOut', 'CircInOut'),
                ('BackIn', 'BackIn', 'BackIn'),
                ('BackOut', 'BackOut', 'BackOut'),
                ('BackInOut', 'BackInOut', 'BackInOut')],
        name='', default='Linear')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmFloatSocket', 'From', default_value=0.0)
        self.add_input('ArmFloatSocket', 'To', default_value=0.0)
        self.add_input('ArmFloatSocket', 'Duration', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Tick')
        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('ArmFloatSocket', 'Value')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property0}'
