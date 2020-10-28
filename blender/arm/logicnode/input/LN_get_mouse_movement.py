from arm.logicnode.arm_nodes import *

class GetMouseMovementNode(ArmLogicTreeNode):
    """Returns the movement coordinates of the mouse."""
    bl_idname = 'LNGetMouseMovementNode'
    bl_label = 'Get Mouse Movement'
    arm_section = 'mouse'
    arm_version = 1

    def init(self, context):
        super(GetMouseMovementNode, self).init(context)
        self.add_input('NodeSocketFloat', 'X Multiplier' , default_value=-1.0)
        self.add_input('NodeSocketFloat', 'Y Multiplier', default_value=-1.0)
        self.add_input('NodeSocketFloat', 'Delta Multiplier', default_value=-1.0)
        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')
        self.add_output('NodeSocketInt', 'Delta')
        self.add_output('NodeSocketFloat', 'Multiplied X')
        self.add_output('NodeSocketFloat', 'Multiplied Y')
        self.add_output('NodeSocketFloat', 'Multiplied Delta')
