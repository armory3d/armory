import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WriteStorageNode(Node, ArmLogicTreeNode):
    '''WriteStorage node'''
    bl_idname = 'LNWriteStorageNode'
    bl_label = 'Write Storage'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Key')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(WriteStorageNode, category='Action')
