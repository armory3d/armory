import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetPropertyNode(Node, ArmLogicTreeNode):
    '''Get property node'''
    bl_idname = 'LNGetPropertyNode'
    bl_label = 'Get Property'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Property')
        self.outputs.new('NodeSocketShader', 'Value')
        self.outputs.new('NodeSocketString', 'Property')

add_node(GetPropertyNode, category='Value')
