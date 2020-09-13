from arm.logicnode.arm_nodes import *


class RandomFloatNode(ArmLogicTreeNode):
    """Random float node"""
    bl_idname = 'LNRandomFloatNode'
    bl_label = 'Random Float'

    def init(self, context):
        self.add_input('NodeSocketFloat', 'Min')
        self.add_input('NodeSocketFloat', 'Max', default_value=1.0)
        # self.add_input('NodeSocketInt', 'Seed')
        self.add_output('NodeSocketFloat', 'Float')


add_node(RandomFloatNode, category=PKG_AS_CATEGORY)
