from arm.logicnode.arm_nodes import *

class DisplayInfoNode(ArmLogicTreeNode):
    """Display info node"""
    bl_idname = 'LNDisplayInfoNode'
    bl_label = 'Display Info'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')

add_node(DisplayInfoNode, category=MODULE_AS_CATEGORY, section='screen')
