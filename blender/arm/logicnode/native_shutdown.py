import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ShutdownNode(Node, ArmLogicTreeNode):
    '''Shutdown node'''
    bl_idname = 'LNShutdownNode'
    bl_label = 'Shutdown'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ShutdownNode, category='Native')
