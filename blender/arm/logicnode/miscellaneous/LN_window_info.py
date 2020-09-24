from arm.logicnode.arm_nodes import *

class WindowInfoNode(ArmLogicTreeNode):
    """Use to get the window resolution."""
    bl_idname = 'LNWindowInfoNode'
    bl_label = 'Window Info'
    arm_version = 1

    def init(self, context):
        super(WindowInfoNode, self).init(context)
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')

add_node(WindowInfoNode, category=PKG_AS_CATEGORY, section='screen')
