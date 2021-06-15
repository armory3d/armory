from arm.logicnode.arm_nodes import *

class SeparateTransformNode(ArmLogicTreeNode):
    """Separates the transform of the given object."""
    bl_idname = 'LNSeparateTransformNode'
    bl_label = 'Separate Transform'
    arm_version = 1

    def init(self, context):
        super(SeparateTransformNode, self).init(context)
        self.add_input('NodeSocketShader', 'Transform')

        self.add_output('NodeSocketVector', 'Location')
        self.add_output('ArmNodeSocketRotation', 'Rotation')
        self.add_output('NodeSocketVector', 'Scale')
