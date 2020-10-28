import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class CallGroupNode(ArmLogicTreeNode):
    """Calls the given group of nodes."""
    bl_idname = 'LNCallGroupNode'
    bl_label = 'Call Node Group'
    arm_section = 'group'
    arm_version = 1

    @property
    def property0(self):
        return arm.utils.safesrc(bpy.data.worlds['Arm'].arm_project_package) + '.node.' + arm.utils.safesrc(self.property0_.name)

    property0_: PointerProperty(name='Group', type=bpy.types.NodeTree)

    def init(self, context):
        super(CallGroupNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_', bpy.data, 'node_groups', icon='NONE', text='')
