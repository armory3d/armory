import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *


class SpawnCollectionNode(ArmLogicTreeNode):
    """Spawns a collection to the current scene."""
    bl_idname = 'LNSpawnCollectionNode'
    bl_label = 'Spawn Collection'
    bl_icon = 'NONE'

    property0: PointerProperty(name='Collection', type=bpy.types.Collection)

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Transform')

        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('ArmNodeSocketArray', 'Top-Level Objects')
        self.outputs.new('ArmNodeSocketArray', 'All Objects')
        self.outputs.new('ArmNodeSocketObject', 'Owner Object')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'collections', icon='NONE', text='')


add_node(SpawnCollectionNode, category=MODULE_AS_CATEGORY, section='collection')
