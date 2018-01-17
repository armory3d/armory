import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class DisplayInfoNode(Node, ArmLogicTreeNode):
    '''Display info node'''
    bl_idname = 'LNDisplayInfoNode'
    bl_label = 'Display Info'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', 'Width')
        self.outputs.new('NodeSocketInt', 'Height')

add_node(DisplayInfoNode, category='Value')
