import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RadToDegNode(Node, ArmLogicTreeNode):
    '''Radians to degrees node'''
    bl_idname = 'LNRadToDegNode'
    bl_label = 'Rad to Deg'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Radians')
        self.outputs.new('NodeSocketFloat', 'Degrees')

add_node(RadToDegNode, category='Value')
