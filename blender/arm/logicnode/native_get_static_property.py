import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetStaticPropertyNode(Node, ArmLogicTreeNode):
    '''Get static property node'''
    bl_idname = 'LNGetStaticPropertyNode'
    bl_label = 'Get Static Property'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketString', 'Class')
        self.inputs.new('NodeSocketString', 'Property')
        self.outputs.new('NodeSocketShader', 'Value')

add_node(GetStaticPropertyNode, category='Native')
