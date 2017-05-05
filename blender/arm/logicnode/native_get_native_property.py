import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetNativePropertyNode(Node, ArmLogicTreeNode):
    '''Get native property node'''
    bl_idname = 'LNGetNativePropertyNode'
    bl_label = 'Get Native Property'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Property')
        self.outputs.new('NodeSocketShader', 'Value')

add_node(GetNativePropertyNode, category='Native')
