import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WaitNode(Node, ArmLogicTreeNode):
    '''Wait node'''
    bl_idname = 'WaitNodeType'
    bl_label = 'Wait'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketFloat', "Time")
        self.outputs.new('NodeSocketShader', "Out")

add_node(WaitNode, category='Operator')
