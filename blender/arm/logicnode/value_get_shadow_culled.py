import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetShadowCulledNode(Node, ArmLogicTreeNode):
    '''Get Shadow Culled node'''
    bl_idname = 'LNGetShadowCulledNode'
    bl_label = 'Get Shadow Culled'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Culled')

add_node(GetShadowCulledNode, category='Value')
