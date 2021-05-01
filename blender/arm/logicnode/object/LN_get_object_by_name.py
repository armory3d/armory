import bpy

from arm.logicnode.arm_nodes import *


class GetObjectNode(ArmLogicTreeNode):
    """Searches for a object that uses the given name in the current active scene and returns it."""
    bl_idname = 'LNGetObjectNode'
    bl_label = 'Get Object by Name'
    arm_version = 1

    property0: PointerProperty(
        type=bpy.types.Scene, name='Scene',
        description='The scene from which to take the object')

    def init(self, context):
        super(GetObjectNode, self).init(context)
        self.add_input('NodeSocketString', 'Name')

        self.add_output('ArmNodeSocketObject', 'Object')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, "scenes")
