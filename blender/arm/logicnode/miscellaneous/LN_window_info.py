from arm.logicnode.arm_nodes import *

class WindowInfoNode(ArmLogicTreeNode):
    """Window info node"""
    bl_idname = 'LNWindowInfoNode'
    bl_label = 'Window Info'
    arm_version = 1

    def init(self, context):
        super(WindowInfoNode, self).init(context)
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')

add_node(WindowInfoNode, category=PKG_AS_CATEGORY, section='screen')
