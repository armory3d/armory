import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GamepadCoordsNode(ArmLogicTreeNode):
    '''Gamepad coords node'''
    bl_idname = 'LNGamepadCoordsNode'
    bl_label = 'Gamepad Coords'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketVector', 'Left Stick')
        self.add_output('NodeSocketVector', 'Right Stick')
        self.add_output('NodeSocketVector', 'Left Movement')
        self.add_output('NodeSocketVector', 'Right Movement')
        self.add_output('NodeSocketFloat', 'Left Trigger')
        self.add_output('NodeSocketFloat', 'Right Trigger')
        self.add_input('NodeSocketInt', 'Gamepad')

add_node(GamepadCoordsNode, category=MODULE_AS_CATEGORY, section='gamepad')
