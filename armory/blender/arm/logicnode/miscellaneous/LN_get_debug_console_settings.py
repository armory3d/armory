from arm.logicnode.arm_nodes import *


class GetDebugConsoleSettings(ArmLogicTreeNode):
    """Return properties of the debug console.

    @output Enabled: Whether the debug console is enabled.
    @output Visible: Whether the debug console is visible,
        or `false` if the debug console is disabled.
    @output Hovered: Whether the debug console is hovered by the mouse cursor,
        or `false` if the debug console is disabled.
    @output UI Scale: The scaling factor of the debug console user interface,
        or `1.0` if the debug console is disabled.
    @output Position: The initial position of the debug console.
        Possible values if the debug console is enabled: `"Left"`, `"Center"`, `"Right"`.
        If the debug console is disabled, the returned value is an empty string `""`.
    """
    bl_idname = 'LNGetDebugConsoleSettings'
    bl_label = 'Get Debug Console Settings'
    arm_version = 2

    def arm_init(self, context):
        self.add_output('ArmBoolSocket', 'Enabled')
        self.add_output('ArmBoolSocket', 'Visible')
        self.add_output('ArmBoolSocket', 'Hovered')
        self.add_output('ArmFloatSocket', 'UI Scale')
        self.add_output('ArmStringSocket', 'Position')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNGetDebugConsoleSettings', self.arm_version, 'LNGetDebugConsoleSettings', 2,
            in_socket_mapping={}, out_socket_mapping={0: 1, 1: 3, 2: 4}
        )
