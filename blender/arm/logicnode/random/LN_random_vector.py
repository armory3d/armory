from arm.logicnode.arm_nodes import *


class RandomVectorNode(ArmLogicTreeNode):
    """Generates a random vector."""
    bl_idname = 'LNRandomVectorNode'
    bl_label = 'Random Vector'
    arm_version = 1

    def init(self, context):
        super(RandomVectorNode, self).init(context)
        self.add_input('NodeSocketVector', 'Min', default_value=[-1.0, -1.0, -1.0])
        self.add_input('NodeSocketVector', 'Max', default_value=[1.0, 1.0, 1.0])
        self.add_output('NodeSocketVector', 'Vector')
