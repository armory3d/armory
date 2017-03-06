import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from logicnode.arm_nodes import *

class InitNode(Node, ArmLogicTreeNode):
    '''Init node'''
    bl_idname = 'InitNodeType'
    bl_label = 'Init'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Out")

add_node(InitNode, category='Event')
