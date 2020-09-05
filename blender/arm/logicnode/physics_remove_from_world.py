import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RemoveFromWorldNode (Node, ArmLogicTreeNode):
    '''Remove From World Node'''
    bl_idname = 'LNRemoveFromWorldNode'
    bl_label = 'Remove From World'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(RemoveFromWorldNode, category='Physics')
