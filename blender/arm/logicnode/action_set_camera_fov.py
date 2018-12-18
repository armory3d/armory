import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetCameraFovNode(Node, ArmLogicTreeNode):
    '''Set camera FOV node'''
    bl_idname = 'LNSetCameraFovNode'
    bl_label = 'Set Camera FOV'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketFloat', 'FOV')
        self.inputs[-1].default_value = 0.85
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetCameraFovNode, category='Action')
