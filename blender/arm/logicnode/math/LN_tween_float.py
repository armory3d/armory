from arm.logicnode.arm_nodes import *

class TweenFloatNode( ArmLogicTreeNode):
    '''Tween a float value'''
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

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmFloatSocket', 'From', default_value = 0.0)
        self.add_input('ArmFloatSocket', 'To', default_value = 0.0)
        self.add_input('ArmFloatSocket', 'Time', default_value = 1.0)
        
        self.add_output('ArmFloatSocket', 'Tween')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Tick')
        self.add_output('ArmNodeSocketAction', 'Done')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
    
    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property0}'