import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ApplyForceNode(Node, ArmLogicTreeNode):
    '''Apply force node'''
    bl_idname = 'LNApplyForceNode'
    bl_label = 'Apply Force'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Force')
        self.inputs.new('NodeSocketBool', 'On Local Axis')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ApplyForceNode, category='Physics')
