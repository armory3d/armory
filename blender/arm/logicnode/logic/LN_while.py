import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WhileNode(ArmLogicTreeNode):
    '''While node'''
    bl_idname = 'LNWhileNode'
    bl_label = 'While'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Condition')
        self.outputs.new('ArmNodeSocketAction', 'Loop')
        self.outputs.new('ArmNodeSocketAction', 'Done')

add_node(WhileNode, category=MODULE_AS_CATEGORY, section='flow')
