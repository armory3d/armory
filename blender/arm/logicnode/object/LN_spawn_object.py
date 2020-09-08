import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SpawnObjectNode(ArmLogicTreeNode):
    """Spawn object node"""
    bl_idname = 'LNSpawnObjectNode'
    bl_label = 'Spawn Object'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_input('NodeSocketBool', 'Children', default_value=True)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(SpawnObjectNode, category=MODULE_AS_CATEGORY)
