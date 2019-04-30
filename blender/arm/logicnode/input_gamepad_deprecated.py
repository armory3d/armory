import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GamepadNode(Node, ArmLogicTreeNode):
    '''Gamepad node'''
    bl_idname = 'LNGamepadNode'
    bl_label = 'Gamepad State (deprecated)'
    bl_icon = 'CURVE_PATH'
    
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

    def init(self, context):
        self.outputs.new('NodeSocketBool', 'State')
        self.inputs.new('NodeSocketInt', 'Gamepad')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(GamepadNode, category='Input')
