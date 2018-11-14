import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ReadJsonNode(Node, ArmLogicTreeNode):
    '''Read JSON node'''
    bl_idname = 'LNReadJsonNode'
    bl_label = 'Read JSON'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'File')
        self.outputs.new('ArmNodeSocketAction', 'Loaded')
        self.outputs.new('NodeSocketShader', 'Dynamic')

add_node(ReadJsonNode, category='Native')
