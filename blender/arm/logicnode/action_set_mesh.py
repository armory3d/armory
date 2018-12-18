import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMeshNode(Node, ArmLogicTreeNode):
    '''Set mesh node'''
    bl_idname = 'LNSetMeshNode'
    bl_label = 'Set Mesh'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Mesh')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMeshNode, category='Action')
