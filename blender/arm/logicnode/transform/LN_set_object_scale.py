from arm.logicnode.arm_nodes import *

class SetScaleNode(ArmLogicTreeNode):
    """Use to set the scale of an object."""
    bl_idname = 'LNSetScaleNode'
    bl_label = 'Set Object Scale'
    arm_version = 1

    def init(self, context):
        super(SetScaleNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Scale', default_value=[1.0, 1.0, 1.0])
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetScaleNode, category=PKG_AS_CATEGORY, section='scale')
