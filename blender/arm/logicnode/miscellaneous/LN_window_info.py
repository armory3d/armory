from arm.logicnode.arm_nodes import *

class WindowInfoNode(ArmLogicTreeNode):
    """Window info node"""
    bl_idname = 'LNWindowInfoNode'
    bl_label = 'Window Info'

    def init(self, context):
        self.add_output('NodeSocketInt', 'Width')
        self.add_output('NodeSocketInt', 'Height')

add_node(WindowInfoNode, category=PKG_AS_CATEGORY, section='screen')
