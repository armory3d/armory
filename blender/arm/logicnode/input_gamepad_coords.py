import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GamepadCoordsNode(Node, ArmLogicTreeNode):
    '''Gamepad coords node'''
    bl_idname = 'LNGamepadCoordsNode'
    bl_label = 'Gamepad Coords'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketVector', 'Left Stick')
        self.outputs.new('NodeSocketVector', 'Right Stick')
        self.outputs.new('NodeSocketVector', 'Left Movement')
        self.outputs.new('NodeSocketVector', 'Right Movement')
        self.outputs.new('NodeSocketFloat', 'Left Trigger')
        self.outputs.new('NodeSocketFloat', 'Right Trigger')
        self.inputs.new('NodeSocketInt', 'Gamepad')

add_node(GamepadCoordsNode, category='Input')
