from arm.logicnode.arm_nodes import *


class RandomFloatNode(ArmLogicTreeNode):
    """Use to generate a random float."""
    bl_idname = 'LNRandomFloatNode'
    bl_label = 'Random Float'
    arm_version = 1

    def init(self, context):
        super(RandomFloatNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Min')
        self.add_input('NodeSocketFloat', 'Max', default_value=1.0)
        # self.add_input('NodeSocketInt', 'Seed')
        self.add_output('NodeSocketFloat', 'Float')


add_node(RandomFloatNode, category=PKG_AS_CATEGORY)
