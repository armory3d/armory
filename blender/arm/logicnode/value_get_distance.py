import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetDistanceNode(Node, ArmLogicTreeNode):
    '''Get distance node'''
    bl_idname = 'LNGetDistanceNode'
    bl_label = 'Get Distance'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketFloat', 'Distance')

add_node(GetDistanceNode, category='Value')
