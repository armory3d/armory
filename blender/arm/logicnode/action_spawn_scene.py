import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SpawnSceneNode(Node, ArmLogicTreeNode):
    '''Spawn scene node'''
    bl_idname = 'LNSpawnSceneNode'
    bl_label = 'Spawn Scene'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Scene')
        self.inputs.new('NodeSocketShader', 'Transform')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketObject', 'Root')

add_node(SpawnSceneNode, category='Action')
