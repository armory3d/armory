import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RemoveActiveSceneNode(Node, ArmLogicTreeNode):
    '''Remove active scene node'''
    bl_idname = 'LNRemoveActiveSceneNode'
    bl_label = 'Remove Active Scene'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(RemoveActiveSceneNode, category='Action')
