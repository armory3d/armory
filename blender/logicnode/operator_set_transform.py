import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from logicnode.arm_nodes import *

class SetTransformNode(Node, ArmLogicTreeNode):
    '''Set transform node'''
    bl_idname = 'SetTransformNodeType'
    bl_label = 'Set Transform'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Object")
        self.inputs.new('NodeSocketShader', "Transform")
        self.outputs.new('NodeSocketShader', "Out")

add_node(SetTransformNode, category='Operator')
