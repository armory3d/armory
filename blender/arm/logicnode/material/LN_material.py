import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class MaterialNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given material as a variable."""
    bl_idname = 'LNMaterialNode'
    bl_label = 'Material'
    arm_version = 1

    @property
    def property0_get(self):
        if self.property0 == None:
            return ''
        if self.property0.name not in bpy.data.materials:
            return self.property0.name
        return arm.utils.asset_name(bpy.data.materials[self.property0.name])

    property0: HaxePointerProperty('property0', name='', type=bpy.types.Material)

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Material', is_var=True)

    def draw_content(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'materials', icon='NONE', text='')

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.property0 = master_node.property0
