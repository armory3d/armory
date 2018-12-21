import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetCameraFovNode(Node, ArmLogicTreeNode):
    '''Get camera FOV node'''
    bl_idname = 'LNGetCameraFovNode'
    bl_label = 'Get Camera FOV'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketFloat', 'FOV')

add_node(GetCameraFovNode, category='Value')
