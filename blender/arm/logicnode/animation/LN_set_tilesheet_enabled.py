from arm.logicnode.arm_nodes import *

class SetTilesheetEnabledNode(ArmLogicTreeNode):
    """Sets the tilesheet enabled state of the given object."""
    bl_idname = 'LNSetTilesheetEnabledNode'
    bl_label = 'Set Tilesheet Enabled'
    arm_version = 1

    def init(self, context):
        super(SetTilesheetEnabledNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketBool', 'Bool')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetTilesheetEnabledNode, category=PKG_AS_CATEGORY, section='tilesheet')
