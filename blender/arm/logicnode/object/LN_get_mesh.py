import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMeshNode(ArmLogicTreeNode):
    '''Get mesh node'''
    bl_idname = 'LNGetMeshNode'
    bl_label = 'Get Mesh'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketShader', 'Mesh')

add_node(GetMeshNode, category=MODULE_AS_CATEGORY, section='props')
