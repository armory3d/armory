import bpy

from arm.logicnode.arm_nodes import *


class SpawnCollectionNode(ArmLogicTreeNode):
    """
    Spawns a new instance of the selected `collection` from the given `scene`. 
    If the `scene` is empty or null, the current active scene is used. Each spawned 
    instance has an empty owner object to control the instance as a whole (like Blender
    uses it for collection instances).

    @input Scene: Scene in which the collection belongs.
    @input Collection: Collection to be spawned.
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
    arm_section = 'collection'
    arm_version = 2

    property0: HaxePointerProperty('property0', name='Collection', type=bpy.types.Collection)

    property1: HaxePointerProperty(
        'property1',
        type=bpy.types.Scene, name='Scene',
        description='The scene from which to take the object')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketArray', 'Top-Level Objects')
        self.add_output('ArmNodeSocketArray', 'All Objects')
        self.add_output('ArmNodeSocketObject', 'Owner Object')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property1', bpy.data, "scenes")
        layout.prop_search(self, 'property0', bpy.data, 'collections', icon='NONE', text='')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)