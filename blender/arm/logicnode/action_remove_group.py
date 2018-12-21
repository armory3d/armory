import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RemoveGroupNode(Node, ArmLogicTreeNode):
    '''Remove Group node'''
    bl_idname = 'LNRemoveGroupNode'
    bl_label = 'Remove Group'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Group')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(RemoveGroupNode, category='Action')
