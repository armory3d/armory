import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetNativePropertyNode(Node, ArmLogicTreeNode):
    '''Set native property node'''
    bl_idname = 'LNSetNativePropertyNode'
    bl_label = 'Set Native Property'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Property')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetNativePropertyNode, category='Native')
