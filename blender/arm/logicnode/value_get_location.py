import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetLocationNode(Node, ArmLogicTreeNode):
    '''Get location node'''
    bl_idname = 'LNGetLocationNode'
    bl_label = 'Get Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Location')

add_node(GetLocationNode, category='Value')
