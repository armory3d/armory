import bpy

from arm.logicnode.arm_nodes import *


class GroupNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNGroupNode'
    bl_label = 'Collection'
    arm_version = 1

    property0: PointerProperty(name='', type=bpy.types.Collection)

    def init(self, context):
        super(GroupNode, self).init(context)
        self.add_output('ArmNodeSocketArray', 'Array')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0', bpy.data, 'collections', icon='NONE', text='')

add_node(GroupNode, category=PKG_AS_CATEGORY, section='collection')
