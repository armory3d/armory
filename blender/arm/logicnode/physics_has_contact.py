import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class HasContactNode(Node, ArmLogicTreeNode):
    '''Has contact node'''
    bl_idname = 'LNHasContactNode'
    bl_label = 'Has Contact'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object 1')
        self.inputs.new('ArmNodeSocketObject', 'Object 2')
        self.outputs.new('NodeSocketBool', 'Bool')

add_node(HasContactNode, category='Physics')
