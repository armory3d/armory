import bpy

from arm.logicnode.arm_nodes import *


class SceneNode(ArmLogicTreeNode):
    """Scene node"""
    bl_idname = 'LNSceneNode'
    bl_label = 'Scene'

    property0_get: PointerProperty(name='', type=bpy.types.Scene)

    def init(self, context):
        self.add_output('NodeSocketShader', 'Scene')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_get', bpy.data, 'scenes', icon='NONE', text='')

add_node(SceneNode, category=PKG_AS_CATEGORY)
