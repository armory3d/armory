from arm.logicnode.arm_nodes import *

class OnInitNode(ArmLogicTreeNode):
    """Activates the output on the first frame of execution of the logic tree."""
    bl_idname = 'LNOnInitNode'
    bl_label = 'On Init'
    arm_version = 1

    def init(self, context):
        super(OnInitNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnInitNode, category=PKG_AS_CATEGORY)
