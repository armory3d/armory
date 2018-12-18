import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class StopAgentNode(Node, ArmLogicTreeNode):
    '''Stop agent node'''
    bl_idname = 'LNStopAgentNode'
    bl_label = 'Stop Agent'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(StopAgentNode, category='Navmesh')
