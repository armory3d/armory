from arm.logicnode.arm_nodes import *

class SeparateVectorNode(ArmLogicTreeNode):
    """Splits the given vector into XYZ values."""
    bl_idname = 'LNSeparateVectorNode'
    bl_label = 'Separate XYZ'
    arm_section = 'vector'
    arm_version = 1

    def init(self, context):
        super(SeparateVectorNode, self).init(context)
        self.add_input('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')
        self.add_output('NodeSocketFloat', 'Z')
