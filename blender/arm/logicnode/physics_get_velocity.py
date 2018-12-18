import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetVelocityNode(Node, ArmLogicTreeNode):
    '''Get velocity node'''
    bl_idname = 'LNGetVelocityNode'
    bl_label = 'Get Velocity'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Linear')
        # self.outputs.new('NodeSocketVector', 'Linear Factor') # TODO
        # self.outputs[-1].default_value = [1.0, 1.0, 1.0]
        self.outputs.new('NodeSocketVector', 'Angular')
        # self.outputs.new('NodeSocketVector', 'Angular Factor') # TODO
        # self.outputs[-1].default_value = [1.0, 1.0, 1.0]

add_node(GetVelocityNode, category='Physics')
