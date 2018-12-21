import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetScaleNode(Node, ArmLogicTreeNode):
    '''Get scale node'''
    bl_idname = 'LNGetScaleNode'
    bl_label = 'Get Scale'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Scale')

add_node(GetScaleNode, category='Value')
