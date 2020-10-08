from arm.logicnode.arm_nodes import *

class PlayActionNode(ArmLogicTreeNode):
    """Plays the given action."""
    bl_idname = 'LNPlayActionNode'
    bl_label = 'Play Action'
    bl_description = "\"Play Action\" node was deprecated. Please recreate the node."
    bl_icon = 'ERROR'
    arm_version = 2

    def init(self, context):
        super(PlayActionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_input('NodeSocketFloat', 'Blend', default_value=0.2)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')

add_node(PlayActionNode, category=PKG_AS_CATEGORY, section='action', is_obsolete=True)
