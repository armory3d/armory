import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ToBoolNode(Node, ArmLogicTreeNode):
    '''To Bool Node'''
    bl_idname = 'LNToBoolNode'
    bl_label = 'To Bool'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('NodeSocketBool', 'Bool')

add_node(ToBoolNode, category='Logic')
