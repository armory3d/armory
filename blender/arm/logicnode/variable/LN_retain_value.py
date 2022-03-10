from arm.logicnode.arm_nodes import *

class RetainValueNode(ArmLogicTreeNode):
    """Retains the input value.

    @input Retain: Retains the value when exeuted.
    @input Value: The value that should be retained.
    """
    bl_idname = 'LNRetainValueNode'
    bl_label = 'Retain Value'
    arm_section = 'set'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Retain')
        self.add_input('ArmDynamicSocket', 'Value', is_var=True)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Value')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            "LNRetainValueNode", self.arm_version,
            "LNRetainValueNode", 2,
            in_socket_mapping={0: 0, 1: 1},
            out_socket_mapping={0: 1, 1: 0},
        )
