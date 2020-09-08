import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WriteStorageNode(ArmLogicTreeNode):
    '''WriteStorage node'''
    bl_idname = 'LNWriteStorageNode'
    bl_label = 'Write Storage'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Key')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(WriteStorageNode, category=MODULE_AS_CATEGORY, section='file')
