from arm.logicnode.arm_nodes import *

class GetTilesheetStateNode(ArmLogicTreeNode):
    """Returns the information about the current tilesheet of the given object.
    
    @output Active Tilesheet: Current active tilesheet.

    @output Active Action: Current action in the tilesheet.

    @output Frame: Frame offset with 0 as the first frame of the active action.

    @output Absolute Frame: Absolute frame index in this tilesheet.

    @output Is Paused: Tilesheet action paused.
    """
    bl_idname = 'LNGetTilesheetStateNode'
    bl_label = 'Get Tilesheet State'
    arm_version = 2
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmStringSocket', 'Active Tilesheet')
        self.add_output('ArmStringSocket', 'Active Action')
        self.add_output('ArmIntSocket', 'Frame')
        self.add_output('ArmIntSocket', 'Absolute Frame')
        self.add_output('ArmBoolSocket', 'Is Paused')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNGetTilesheetStateNode', self.arm_version, 'LNGetTilesheetStateNode', 2,
            in_socket_mapping={}, out_socket_mapping={0:1, 1:3, 2:4}
        )
