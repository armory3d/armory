import bpy

from arm.logicnode.arm_nodes import *


class MeshNode(ArmLogicTreeNode):
    """Stores the given mesh as a variable."""
    bl_idname = 'LNMeshNode'
    bl_label = 'Mesh'
    arm_version = 1

    property0_get: HaxePointerProperty('property0_get', name='', type=bpy.types.Mesh)

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Mesh', is_var=True)

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_get', bpy.data, 'meshes', icon='NONE', text='')
