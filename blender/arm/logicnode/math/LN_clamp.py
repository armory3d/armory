from arm.logicnode.arm_nodes import *

class ClampNode(ArmLogicTreeNode):
    """Keeps the value inside the given bound."""
    bl_idname = 'LNClampNode'
    bl_label = 'Clamp'
    arm_version = 1

    def init(self, context):
        super(ClampNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Value')
        self.add_input('NodeSocketFloat', 'Min')
        self.add_input('NodeSocketFloat', 'Max')
        self.add_output('NodeSocketFloat', 'Result')
