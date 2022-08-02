import bpy

from arm.logicnode.arm_nodes import *


class SceneNode(ArmLogicTreeNode):
    """Stores the given scene as a variable."""
    bl_idname = 'LNSceneNode'
    bl_label = 'Scene'
    arm_version = 1

    property0_get: HaxePointerProperty('property0_get', name='', type=bpy.types.Scene)

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Scene')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_get', bpy.data, 'scenes', icon='NONE', text='')
