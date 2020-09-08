from arm.logicnode.arm_nodes import *


class RandomBooleanNode(ArmLogicTreeNode):
    """Random boolean node"""
    bl_idname = 'LNRandomBooleanNode'
    bl_label = 'Random Boolean'

    def init(self, context):
        self.add_output('NodeSocketBool', 'Bool')


add_node(RandomBooleanNode, category=MODULE_AS_CATEGORY)
