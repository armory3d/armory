from arm.logicnode.arm_nodes import *


class RandomVectorNode(ArmLogicTreeNode):
    """Use to generate a random vector."""
    bl_idname = 'LNRandomVectorNode'
    bl_label = 'Random Vector'
    arm_version = 1

    def init(self, context):
        super(RandomVectorNode, self).init(context)
        self.add_input('NodeSocketVector', 'Min', default_value=[-1.0, -1.0, -1.0])
        self.add_input('NodeSocketVector', 'Max', default_value=[1.0, 1.0, 1.0])
        self.add_output('NodeSocketVector', 'Vector')


add_node(RandomVectorNode, category=PKG_AS_CATEGORY)
