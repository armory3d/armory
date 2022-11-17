from arm.logicnode.arm_nodes import *


class SeparateColorNode(ArmLogicTreeNode):
    """Splits the given color into its RGBA components (red, green, blue, and alpha).
    If the input color is `null`, the outputs are each set to `0.0`.
    """
    bl_idname = 'LNSeparateColorNode'
    bl_label = 'Separate RGBA'
    arm_section = 'color'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmFloatSocket', 'R')
        self.add_output('ArmFloatSocket', 'G')
        self.add_output('ArmFloatSocket', 'B')
        self.add_output('ArmFloatSocket', 'A')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
