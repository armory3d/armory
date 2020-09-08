import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class NotNode(ArmLogicTreeNode):
    '''Not node'''
    bl_idname = 'LNNotNode'
    bl_label = 'Not'
    bl_icon = 'NONE'
    
    def init(self, context):
        self.inputs.new('NodeSocketBool', 'Value')
        self.outputs.new('NodeSocketBool', 'Value')

add_node(NotNode, category=MODULE_AS_CATEGORY)
