import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MouseCoordsNode(Node, ArmLogicTreeNode):
    '''Mouse coords node'''
    bl_idname = 'LNMouseCoordsNode'
    bl_label = 'Mouse Coords'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketVector', 'Coords')
        self.outputs.new('NodeSocketVector', 'Movement')
        self.outputs.new('NodeSocketInt', 'Wheel')

add_node(MouseCoordsNode, category='Input')
