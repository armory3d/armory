import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SceneNode(Node, ArmLogicTreeNode):
    '''Scene node'''
    bl_idname = 'LNSceneNode'
    bl_label = 'Scene'
    bl_icon = 'QUESTION'

    property0_get: PointerProperty(name='', type=bpy.types.Scene)

    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Scene')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_get', bpy.data, 'scenes', icon='NONE', text='')

add_node(SceneNode, category='Variable')
