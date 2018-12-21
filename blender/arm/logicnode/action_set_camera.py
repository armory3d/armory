import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetCameraNode(Node, ArmLogicTreeNode):
    '''Set camera node'''
    bl_idname = 'LNSetCameraNode'
    bl_label = 'Set Camera'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetCameraNode, category='Action')
