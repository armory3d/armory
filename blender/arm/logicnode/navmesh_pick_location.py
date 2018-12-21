import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PickLocationNode(Node, ArmLogicTreeNode):
    '''Pick location node'''
    bl_idname = 'LNPickLocationNode'
    bl_label = 'Pick Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Navmesh')
        self.inputs.new('NodeSocketVector', 'Screen Coords')
        self.outputs.new('NodeSocketVector', 'Location')

add_node(PickLocationNode, category='Navmesh')
