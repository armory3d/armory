import bpy

from arm.logicnode.arm_nodes import *


class SpawnCollectionNode(ArmLogicTreeNode):
    """
    Spawns a new instance of the selected collection. Each spawned instance 
    has an empty owner object to control the instance as a whole (like Blender 
    uses it for collection instances).

    @input In: activates the node.
    @input Transform: the transformation of the instance that should be
        spawned. Please note that the collection's instance offset is
        also taken into account.

    @output Out: activated when a collection instance was spawned. It is
        not activated when no collection is selected.
    @output Top-Level Objects: all objects in the last spawned
        collection that are direct children of the owner object of the
        collection's instance.
    @output All Objects: all objects in the last spawned collection.
    @output Owner Object: The owning object of the last spawned
        collection's instance.
    """
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
