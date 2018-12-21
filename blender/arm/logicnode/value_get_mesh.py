import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMeshNode(Node, ArmLogicTreeNode):
    '''Get mesh node'''
    bl_idname = 'LNGetMeshNode'
    bl_label = 'Get Mesh'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketShader', 'Mesh')

add_node(GetMeshNode, category='Value')
