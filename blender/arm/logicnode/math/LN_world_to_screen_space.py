from arm.logicnode.arm_nodes import *

class WorldToScreenSpaceNode(ArmLogicTreeNode):
    """World to screen space node"""
    bl_idname = 'LNWorldToScreenSpaceNode'
    bl_label = 'World To Screen Space'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketVector', 'Vector')

add_node(WorldToScreenSpaceNode, category=MODULE_AS_CATEGORY, section='matrix')
