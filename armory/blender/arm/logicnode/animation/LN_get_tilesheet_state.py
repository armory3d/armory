from arm.logicnode.arm_nodes import *

class GetTilesheetStateNode(ArmLogicTreeNode):
    """Returns the information about the current tilesheet of the given object.

    @output Tilesheet: Tilesheet name.

    @output Active Action: Current action in the tilesheet.

    @output Frame: Frame offset with 0 as the first frame of the active action.

    @output Absolute Frame: Absolute frame index in this tilesheet.

    @output Is Paused: Tilesheet action paused.
    """
    bl_idname = 'LNGetTilesheetStateNode'
    bl_label = 'Get Tilesheet State'
    arm_version = 4
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmStringSocket', 'Tilesheet')
        self.add_output('ArmStringSocket', 'Active Action')
        self.add_output('ArmIntSocket', 'Frame')
        self.add_output('ArmIntSocket', 'Absolute Frame')
        self.add_output('ArmBoolSocket', 'Is Paused')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version in (0, 1):
            return NodeReplacement(
                'LNGetTilesheetStateNode', self.arm_version, 'LNGetTilesheetStateNode', 4,
                in_socket_mapping={}, out_socket_mapping={0: 1, 1: 3, 2: 4}
            )
        elif self.arm_version in (2, 3):
            # Version 2 and 3 have same outputs, just rename Material to Tilesheet
            return NodeReplacement(
                'LNGetTilesheetStateNode', self.arm_version, 'LNGetTilesheetStateNode', 4,
                in_socket_mapping={0: 0}, out_socket_mapping={0: 0, 1: 1, 2: 2, 3: 3, 4: 4}
            )
        raise LookupError()
