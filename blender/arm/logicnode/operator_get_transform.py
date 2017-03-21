import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetTransformNode(Node, ArmLogicTreeNode):
    '''Get transform node'''
    bl_idname = 'GetTransformNodeType'
    bl_label = 'Get Transform'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Object")
        self.outputs.new('NodeSocketShader', "Out")
        self.outputs.new('NodeSocketShader', "Transform")

add_node(GetTransformNode, category='Operator')
