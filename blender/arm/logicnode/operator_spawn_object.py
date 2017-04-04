import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SpawnObjectNode(Node, ArmLogicTreeNode):
    '''Spawn object node'''
    bl_idname = 'LNSpawnObjectNode'
    bl_label = 'Spawn Object'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketShader', "Object")
        self.inputs.new('NodeSocketShader', "Tansform")
        self.outputs.new('NodeSocketShader', "Out")
        self.outputs.new('NodeSocketShader', "Object")

add_node(SpawnObjectNode, category='Operator')
