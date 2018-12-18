import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ActiveCameraNode(Node, ArmLogicTreeNode):
    '''Active camera node'''
    bl_idname = 'LNActiveCameraNode'
    bl_label = 'Active Camera'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(ActiveCameraNode, category='Value')
