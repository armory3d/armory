from arm.logicnode.arm_nodes import *

class GetChildrenNode(ArmLogicTreeNode):
    """Use to get the children of an object."""
    bl_idname = 'LNGetChildrenNode'
    bl_label = 'Get Children'
    arm_version = 1

    def init(self, context):
        super(GetChildrenNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Parent')
        self.add_output('ArmNodeSocketArray', 'Children')

add_node(GetChildrenNode, category=PKG_AS_CATEGORY, section='relations')
