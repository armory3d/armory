import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SpawnObjectNode(Node, ArmLogicTreeNode):
    '''Spawn object node'''
    bl_idname = 'LNSpawnObjectNode'
    bl_label = 'Spawn Object'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Transform')
        self.inputs.new('NodeSocketBool', 'Children')
        self.inputs[-1].default_value = True
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(SpawnObjectNode, category='Action')
