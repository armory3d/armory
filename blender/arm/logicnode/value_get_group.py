import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetGroupNode(Node, ArmLogicTreeNode):
    '''Get group node'''
    bl_idname = 'LNGetGroupNode'
    bl_label = 'Get Collection'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketString', 'Name')
        self.outputs.new('ArmNodeSocketArray', 'Array')

add_node(GetGroupNode, category='Value')
