import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnActionMarkerNode(Node, ArmLogicTreeNode):
    '''On action marker node'''
    bl_idname = 'LNOnActionMarkerNode'
    bl_label = 'On Action Marker'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Marker')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(OnActionMarkerNode, category='Animation')
