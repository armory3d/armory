import bpy

from arm.logicnode.arm_nodes import *


class GetObjectNode(ArmLogicTreeNode):
    """Get object node"""
    bl_idname = 'LNGetObjectNode'
    bl_label = 'Get Object'
    bl_icon = 'NONE'

    property0: PointerProperty(
        type=bpy.types.Scene, name='Scene',
        description='The scene from which to take the object')

    def init(self, context):
        self.add_input('NodeSocketString', 'Name')
        self.add_output('ArmNodeSocketObject', 'Object')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, "scenes")

add_node(GetObjectNode, category=MODULE_AS_CATEGORY)
