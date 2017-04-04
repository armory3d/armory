import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class InputCoordsNode(Node, ArmLogicTreeNode):
    '''Input coords node'''
    bl_idname = 'LNInputCoordsNode'
    bl_label = 'Input Coords'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketVector', 'Coords')
        self.outputs.new('NodeSocketVector', 'Movement')

add_node(InputCoordsNode, category='Value')
