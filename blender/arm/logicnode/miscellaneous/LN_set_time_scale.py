from arm.logicnode.arm_nodes import *

class SetTimeScaleNode(ArmLogicTreeNode):
    """Use to set the global time scale."""
    bl_idname = 'LNSetTimeScaleNode'
    bl_label = 'Set Time Scale'
    arm_version = 1

    def init(self, context):
        super(SetTimeScaleNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Scale', default_value=1.0)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetTimeScaleNode, category=PKG_AS_CATEGORY)
