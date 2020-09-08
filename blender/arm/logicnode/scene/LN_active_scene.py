import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ActiveSceneNode(ArmLogicTreeNode):
    '''Active scene node'''
    bl_idname = 'LNActiveSceneNode'
    bl_label = 'Active Scene'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Scene')

add_node(ActiveSceneNode, category=MODULE_AS_CATEGORY)
