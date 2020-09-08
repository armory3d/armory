from arm.logicnode.arm_nodes import *

class SetActionSpeedNode(ArmLogicTreeNode):
    """Set action speed node"""
    bl_idname = 'LNSetActionSpeedNode'
    bl_label = 'Set Action Speed'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketFloat', 'Speed', default_value=1.0)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetActionSpeedNode, category=MODULE_AS_CATEGORY)
