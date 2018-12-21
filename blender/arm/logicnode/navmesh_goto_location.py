import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GoToLocationNode(Node, ArmLogicTreeNode):
    '''Navigate to location node'''
    bl_idname = 'LNGoToLocationNode'
    bl_label = 'Go To Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Location')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(GoToLocationNode, category='Navmesh')
