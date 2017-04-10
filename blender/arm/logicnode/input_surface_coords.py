import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SurfaceCoordsNode(Node, ArmLogicTreeNode):
    '''Surface coords node'''
    bl_idname = 'LNSurfaceCoordsNode'
    bl_label = 'Surface Coords'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketVector', 'Coords')
        self.outputs.new('NodeSocketVector', 'Movement')

add_node(SurfaceCoordsNode, category='Input')
