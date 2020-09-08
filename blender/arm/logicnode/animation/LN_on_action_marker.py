import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnActionMarkerNode(ArmLogicTreeNode):
    '''On action marker node'''
    bl_idname = 'LNOnActionMarkerNode'
    bl_label = 'On Action Marker'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Marker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnActionMarkerNode, category=MODULE_AS_CATEGORY, section='armature')
