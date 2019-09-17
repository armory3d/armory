import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LoadUrlNode(Node, ArmLogicTreeNode):
    '''Load Url'''
    bl_idname = 'LNLoadUrlNode'
    bl_label = 'Load Url (Browser only)'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'URL')

add_node(LoadUrlNode, category='Native')
