from arm.logicnode.arm_nodes import *

class SetActionSpeedNode(ArmLogicTreeNode):
    """Sets the current action playback speed of the given object."""
    bl_idname = 'LNSetActionSpeedNode'
    bl_label = 'Set Action Speed'
    arm_version = 1

    def init(self, context):
        super(SetActionSpeedNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketFloat', 'Speed', default_value=1.0)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetActionSpeedNode, category=PKG_AS_CATEGORY, section='action')
