from arm.logicnode.arm_nodes import *

class ScaleObjectNode(ArmLogicTreeNode):
    """Deprecated. 'Use Set Object Scale' instead."""
    bl_idname = 'LNScaleObjectNode'
    bl_label = 'Scale Object'
    arm_version = 1

    def init(self, context):
        super(ScaleObjectNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Scale')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ScaleObjectNode, category=PKG_AS_CATEGORY, section='scale')
