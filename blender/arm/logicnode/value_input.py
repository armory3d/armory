import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class InputNode(Node, ArmLogicTreeNode):
    '''Input node'''
    bl_idname = 'InputNodeType'
    bl_label = 'Input'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketBool', "Down")

add_node(InputNode, category='Value')
