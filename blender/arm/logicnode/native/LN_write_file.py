import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WriteFileNode(Node, ArmLogicTreeNode):
    '''Write File node'''
    bl_idname = 'LNWriteFileNode'
    bl_label = 'Write File'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'File')
        self.inputs.new('NodeSocketString', 'String')

add_node(WriteFileNode, category=MODULE_AS_CATEGORY, section='file')
