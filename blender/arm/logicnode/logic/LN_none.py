from arm.logicnode.arm_nodes import *

class NoneNode(ArmLogicTreeNode):
    """A null value that can be used in comparisons and conditions."""
    bl_idname = 'LNNoneNode'
    bl_label = 'None'
    arm_version = 1

    def init(self, context):
        super(NoneNode, self).init(context)
        self.add_output('NodeSocketShader', 'None')

add_node(NoneNode, category=PKG_AS_CATEGORY)
