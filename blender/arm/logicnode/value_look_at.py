import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LookAtNode(Node, ArmLogicTreeNode):
    '''Look at node'''
    bl_idname = 'LNLookAtNode'
    bl_label = 'Look At'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'From Location')
        self.inputs.new('NodeSocketVector', 'To Location')
        self.outputs.new('NodeSocketVector', 'Rotation')

add_node(LookAtNode, category='Value')
