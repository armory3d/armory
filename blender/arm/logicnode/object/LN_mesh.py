import bpy

from arm.logicnode.arm_nodes import *


class MeshNode(ArmLogicTreeNode):
    """Mesh node"""
    bl_idname = 'LNMeshNode'
    bl_label = 'Mesh'

    property0_get: PointerProperty(name='', type=bpy.types.Mesh)

    def init(self, context):
        self.add_output('NodeSocketShader', 'Mesh', is_var=True)

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_get', bpy.data, 'meshes', icon='NONE', text='')

add_node(MeshNode, category=MODULE_AS_CATEGORY)
