import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GoToLocationNode(Node, ArmLogicTreeNode):
    '''Navigate to location node'''
    bl_idname = 'GoToLocationNodeType'
    bl_label = 'Go To Location'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Object")
        self.inputs.new('NodeSocketShader', "Location")
        self.outputs.new('NodeSocketShader', "Out")

add_node(GoToLocationNode, category='Operator')
