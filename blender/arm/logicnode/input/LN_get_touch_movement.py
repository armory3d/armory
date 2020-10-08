from arm.logicnode.arm_nodes import *

class GetTouchMovementNode(ArmLogicTreeNode):
    """Returns the movement values of the current touch event."""
    bl_idname = 'LNGetTouchMovementNode'
    bl_label = 'Get Touch Movement'
    arm_version = 1

    def init(self, context):
        super(GetTouchMovementNode, self).init(context)
        self.add_input('NodeSocketFloat', 'X Multiplier', default_value=1.0)
        self.add_input('NodeSocketFloat', 'Y Multiplier', default_value=-1.0)
        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')
        self.add_output('NodeSocketFloat', 'Multiplied X')
        self.add_output('NodeSocketFloat', 'Multiplied Y')

add_node(GetTouchMovementNode, category=PKG_AS_CATEGORY, section='surface')
