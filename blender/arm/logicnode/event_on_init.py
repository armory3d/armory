import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnInitNode(Node, ArmLogicTreeNode):
    '''On init node'''
    bl_idname = 'LNOnInitNode'
    bl_label = 'On Init'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(OnInitNode, category='Event')
