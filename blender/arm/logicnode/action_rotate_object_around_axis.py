import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RotateObjectAroundAxisNode(Node, ArmLogicTreeNode):
    '''Rotate object around axis node'''
    bl_idname = 'LNRotateObjectAroundAxisNode'
    bl_label = 'Rotate Object Around Axis'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Axis')
        self.inputs[-1].default_value = [0, 0, 1]
        self.inputs.new('NodeSocketFloat', 'Angle')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(RotateObjectAroundAxisNode, category='Action')
