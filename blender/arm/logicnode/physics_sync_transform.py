import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SyncTransformNode (Node, ArmLogicTreeNode):
    '''Sync Transform Node'''
    bl_idname = 'LNSyncTransformNode'
    bl_label = 'Sync Transform'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SyncTransformNode, category='Physics')
