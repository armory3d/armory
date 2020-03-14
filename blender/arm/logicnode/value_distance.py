import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class DistanceNode(Node, ArmLogicTreeNode):
    '''Distance node'''
    bl_idname = 'LNDistanceNode'
    bl_label = 'Distance'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Vector')
        self.inputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('NodeSocketFloat', 'Distance')

add_node(DistanceNode, category='Value')
