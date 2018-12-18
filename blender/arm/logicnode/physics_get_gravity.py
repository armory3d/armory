import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetGravityNode(Node, ArmLogicTreeNode):
    '''Get Gravity node'''
    bl_idname = 'LNGetGravityNode'
    bl_label = 'Get Gravity'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Gravity')

add_node(GetGravityNode, category='Physics')
