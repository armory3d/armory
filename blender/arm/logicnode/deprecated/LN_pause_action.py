from arm.logicnode.arm_nodes import *

class PauseActionNode(ArmLogicTreeNode):
    """Pauses the given action."""
    bl_idname = 'LNPauseActionNode'
    bl_label = 'Pause Action'
    bl_description = "Please use the \"Set Action Enabled\" node instead"
    bl_icon='ERROR'
    arm_version = 2

    def init(self, context):
        super(PauseActionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseActionNode, category=PKG_AS_CATEGORY, section='action' is_obsolete=True)
