from arm.logicnode.arm_nodes import *


class ValueChangedNode(ArmLogicTreeNode):
    """Upon activation through the `In` input, this node checks whether
    the given value is different than the value from the last execution
    of this node.

    @output Changed: Activates if the value has changed compared to the
        last time the node was executed or if the node is executed for
        the first time and there is no value for comparison yet.
    @output Unchanged: Activates if the value is the same as it was when
        the node was executed the last time.
    @output Is Initial: Activates if the value is equal to the value at
        the first time the node was executed or if the node is executed
        for the first time. This output works independently of the
        `Changed` or `Unchanged` outputs.
    """
    bl_idname = 'LNValueChangedNode'
    bl_label = 'Value Changed'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Changed')
        self.add_output('ArmNodeSocketAction', 'Unchanged')
        self.add_output('ArmNodeSocketAction', 'Is Initial')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNValueChangedNode', self.arm_version, 'LNValueChangedNode', 2,
            in_socket_mapping={0: 0, 1: 1}, out_socket_mapping={0: 0, 1: 2}
        )
