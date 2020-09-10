import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMeshVisibleNode(Node, ArmLogicTreeNode):
    """Set Mesh Visible node"""
    bl_idname = 'LNSetMeshVisibleNode'
    bl_label = 'Set Mesh Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Visible')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMeshVisibleNode, category='Action')
