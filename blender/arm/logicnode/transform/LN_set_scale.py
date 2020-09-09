from arm.logicnode.arm_nodes import *

class SetScaleNode(ArmLogicTreeNode):
    """Set scale node"""
    bl_idname = 'LNSetScaleNode'
    bl_label = 'Set Scale'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Scale')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetScaleNode, category=PKG_AS_CATEGORY, section='scale')
