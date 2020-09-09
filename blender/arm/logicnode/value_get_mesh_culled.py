import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMeshCulledNode(Node, ArmLogicTreeNode):
    '''Get Mesh Culled node'''
    bl_idname = 'LNGetMeshCulledNode'
    bl_label = 'Get Mesh Culled'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Culled')

add_node(GetMeshCulledNode, category='Value')
