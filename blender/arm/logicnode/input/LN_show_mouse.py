import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ShowMouseNode(ArmLogicTreeNode):
    '''Show Mouse node'''
    bl_idname = 'LNShowMouseNode'
    bl_label = 'Show Mouse'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Show')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ShowMouseNode, category=MODULE_AS_CATEGORY, section='mouse')
