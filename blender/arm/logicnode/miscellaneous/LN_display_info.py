from arm.logicnode.arm_nodes import *

class DisplayInfoNode(ArmLogicTreeNode):
    """Use to get the display resolution. You may be searching for 'Get Window Info' node."""
    bl_idname = 'LNDisplayInfoNode'
    bl_label = 'Display Info'
    arm_version = 1

    def init(self, context):
        super(DisplayInfoNode, self).init(context)
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')

add_node(DisplayInfoNode, category=PKG_AS_CATEGORY, section='screen')
