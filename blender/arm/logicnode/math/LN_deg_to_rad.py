from arm.logicnode.arm_nodes import *

class DegToRadNode(ArmLogicTreeNode):
    """Converts degrees to radians."""
    bl_idname = 'LNDegToRadNode'
    bl_label = 'Deg to Rad'
    arm_version = 1
    arm_section = 'angle'

    def init(self, context):
        super(DegToRadNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Degrees')

        self.add_output('NodeSocketFloat', 'Radians')
