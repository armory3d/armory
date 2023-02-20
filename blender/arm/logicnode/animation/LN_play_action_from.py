from arm.logicnode.arm_nodes import *


class PlayActionFromNode(ArmLogicTreeNode):
    """
    Plays animation action, that starts from given frame, and ends at given frame.

    @input In: Activates the node logic.
    @input Object: States object/armature to run the animation action on.
    @input Action: States animation action to be played.
    @input Start Frame: Sets frame the animation should start at.
    @input End Frame: Sets frame the animation should end at. HINT: Set to "-1" if you want the total frames length of the animation.
    @input Blend: Sets rate to blend multiple animations together.
    @input Speed: Sets rate the animation plays at.
    @input Loop: Sets whether the animation should rewind itself after finishing.

    @output Out: Executes whenever the node is run.
    @output Done: Executes whenever the played animation is finished. (Only triggers if looping is false.)
    """
    bl_idname = 'LNPlayActionFromNode'
    bl_label = 'Play Action From'
    arm_version = 4

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_input('ArmIntSocket', 'Start Frame')
        self.add_input('ArmIntSocket', 'End Frame')
        self.add_input('ArmFloatSocket', 'Blend', default_value = 0.25)
        self.add_input('ArmFloatSocket', 'Speed', default_value = 1.0)
        self.add_input('ArmBoolSocket', 'Loop', default_value = False)
        self.add_input('ArmBoolSocket', 'Reverse', default_value = False)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version in (0, 1):
            return NodeReplacement(
                'LNPlayActionFromNode', self.arm_version, 'LNPlayActionFromNode', 2,
                in_socket_mapping={0:0, 1:1, 2:2, 3:3, 4:4}, out_socket_mapping={0:0, 1:1}
            )

        if self.arm_version == 2:
            return NodeReplacement(
                'LNPlayActionFromNode', self.arm_version, 'LNPlayActionFromNode', 3,
                in_socket_mapping={0:0, 1:1, 2:2, 3:3, 4:5, 5:6, 6:7}, out_socket_mapping={0:0, 1:1}
            )

        raise LookupError()
