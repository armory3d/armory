from arm.logicnode.arm_nodes import *


class RandomColorNode(ArmLogicTreeNode):
    """Random color node"""
    bl_idname = 'LNRandomColorNode'
    bl_label = 'Random Color'
    arm_version = 1

    def init(self, context):
        super(RandomColorNode, self).init(context)
        self.add_output('NodeSocketColor', 'Color')


add_node(RandomColorNode, category=PKG_AS_CATEGORY)
