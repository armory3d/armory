from arm.logicnode.arm_nodes import *


class RandomVectorNode(ArmLogicTreeNode):
    """Random vector node"""
    bl_idname = 'LNRandomVectorNode'
    bl_label = 'Random Vector'

    def init(self, context):
        self.add_input('NodeSocketVector', 'Min', default_value=[-1.0, -1.0, -1.0])
        self.add_input('NodeSocketVector', 'Max', default_value=[1.0, 1.0, 1.0])
        self.add_output('NodeSocketVector', 'Vector')


add_node(RandomVectorNode, category=MODULE_AS_CATEGORY)
