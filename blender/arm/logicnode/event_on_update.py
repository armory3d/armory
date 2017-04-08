import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnUpdateNode(Node, ArmLogicTreeNode):
    '''On update node'''
    bl_idname = 'LNOnUpdateNode'
    bl_label = 'On Update'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(OnUpdateNode, category='Event')
