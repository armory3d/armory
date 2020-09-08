import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMeshNode(ArmLogicTreeNode):
    '''Set mesh node'''
    bl_idname = 'LNSetMeshNode'
    bl_label = 'Set Mesh'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Mesh')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMeshNode, category=MODULE_AS_CATEGORY, section='props')
