import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetObjectCulledNode(Node, ArmLogicTreeNode):
    '''Get Object Culled node'''
    bl_idname = 'LNGetObjectCulledNode'
    bl_label = 'Get Object Culled'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Culled')

add_node(GetObjectCulledNode, category='Value')
