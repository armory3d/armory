from arm.logicnode.arm_nodes import *

class AnimActionNode(ArmLogicTreeNode):
    """Anim action node"""
    bl_idname = 'LNAnimActionNode'
    bl_label = 'Action'
    arm_version = 1

    def init(self, context):
        super(AnimActionNode, self).init(context)
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_output('ArmNodeSocketAnimAction', 'Action', is_var=True)

add_node(AnimActionNode, category=PKG_AS_CATEGORY)
