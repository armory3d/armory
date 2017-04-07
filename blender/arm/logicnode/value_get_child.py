import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetChildNode(Node, ArmLogicTreeNode):
    '''Get child node'''
    bl_idname = 'LNGetChildNode'
    bl_label = 'Get Child'
    bl_icon = 'GAME'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Child')
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(GetChildNode, category='Value')
