import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ObjectNode(ArmLogicTreeNode):
    '''Object node'''
    bl_idname = 'LNObjectNode'
    bl_label = 'Object'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(ObjectNode, category=MODULE_AS_CATEGORY)
