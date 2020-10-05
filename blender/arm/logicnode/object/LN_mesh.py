import bpy

from arm.logicnode.arm_nodes import *


class MeshNode(ArmLogicTreeNode):
    """Stores the given mesh as a variable."""
    bl_idname = 'LNMeshNode'
    bl_label = 'Mesh'
    arm_version = 1

    property0_get: PointerProperty(name='', type=bpy.types.Mesh)

    def init(self, context):
        super(MeshNode, self).init(context)
        self.add_output('NodeSocketShader', 'Mesh', is_var=True)

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_get', bpy.data, 'meshes', icon='NONE', text='')

add_node(MeshNode, category=PKG_AS_CATEGORY)
