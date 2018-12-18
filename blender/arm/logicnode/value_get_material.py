import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetMaterialNode(Node, ArmLogicTreeNode):
    '''Get material node'''
    bl_idname = 'LNGetMaterialNode'
    bl_label = 'Get Material'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketShader', 'Material')

add_node(GetMaterialNode, category='Value')
