import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMeshVisibleNode(Node, ArmLogicTreeNode):
    """Get Mesh Visible node"""
    bl_idname = 'LNGetMeshVisibleNode'
    bl_label = 'Get Mesh Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Visible')

add_node(GetMeshVisibleNode, category='Value')
