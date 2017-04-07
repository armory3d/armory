import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PickObjectNode(Node, ArmLogicTreeNode):
    '''Pick closest object node'''
    bl_idname = 'LNPickObjectNode'
    bl_label = 'Pick Object'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Screen Coords')
        self.outputs.new('ArmNodeSocketObject', 'Object')

add_node(PickObjectNode, category='Physics')
