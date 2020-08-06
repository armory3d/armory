import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ReadFileNode(Node, ArmLogicTreeNode):
    '''Read File node'''
    bl_idname = 'LNReadFileNode'
    bl_label = 'Read File'
    bl_icon = 'NONE'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'File')
        self.inputs.new('NodeSocketBool', 'Use cache')
        self.inputs[-1].default_value = 1
        self.outputs.new('ArmNodeSocketAction', 'Loaded')
        self.outputs.new('NodeSocketString', 'String')

add_node(ReadFileNode, category='Native')
