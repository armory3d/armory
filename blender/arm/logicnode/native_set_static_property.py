import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetStaticPropertyNode(Node, ArmLogicTreeNode):
    '''Set static property node'''
    bl_idname = 'LNSetStaticPropertyNode'
    bl_label = 'Set Static Property'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Class')
        self.inputs.new('NodeSocketString', 'Property')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetStaticPropertyNode, category='Native')
