import bpy

from arm.logicnode.arm_nodes import *


class SpawnCollectionNode(ArmLogicTreeNode):
    """Spawns a collection to the current scene."""
    bl_idname = 'LNSpawnCollectionNode'
    bl_label = 'Spawn Collection'
    arm_version = 1

    property0: PointerProperty(name='Collection', type=bpy.types.Collection)

    def init(self, context):
        super(SpawnCollectionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Transform')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketArray', 'Top-Level Objects')
        self.add_output('ArmNodeSocketArray', 'All Objects')
        self.add_output('ArmNodeSocketObject', 'Owner Object')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'collections', icon='NONE', text='')


add_node(SpawnCollectionNode, category=PKG_AS_CATEGORY, section='collection')
