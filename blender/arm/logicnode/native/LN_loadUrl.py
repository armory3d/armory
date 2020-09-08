import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LoadUrlNode(ArmLogicTreeNode):
    '''Load Url'''
    bl_idname = 'LNLoadUrlNode'
    bl_label = 'Load Url (Browser only)'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'URL')

add_node(LoadUrlNode, category=MODULE_AS_CATEGORY)
