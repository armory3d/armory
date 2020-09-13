import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class CallGroupNode(ArmLogicTreeNode):
    """Call group node"""
    bl_idname = 'LNCallGroupNode'
    bl_label = 'Call Node Group'

    @property
    def property0(self):
        return arm.utils.safesrc(bpy.data.worlds['Arm'].arm_project_package) + '.node.' + arm.utils.safesrc(self.property0_.name)

    property0_: PointerProperty(name='Group', type=bpy.types.NodeTree)

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_', bpy.data, 'node_groups', icon='NONE', text='')

add_node(CallGroupNode, category=PKG_AS_CATEGORY, section='group')
