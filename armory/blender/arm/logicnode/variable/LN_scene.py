import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class SceneNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given scene as a variable."""
    bl_idname = 'LNSceneNode'
    bl_label = 'Scene'
    arm_version = 2

    @property
    def property0_get(self):
        if self.property0 == None:
            return ''
        if self.property0.name not in bpy.data.scenes:
            return self.property0.name
        return arm.utils.asset_name(bpy.data.scenes[self.property0.name])

    property0: HaxePointerProperty('property0', name='', type=bpy.types.Scene)

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Scene', is_var=True)

    def draw_content(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'scenes', icon='NONE', text='')

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.property0 = master_node.property0

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
