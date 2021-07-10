from arm.logicnode.arm_nodes import *

class RadToDegNode(ArmLogicTreeNode):
    """Converts radians to degrees."""
    bl_idname = 'LNRadToDegNode'
    bl_label = 'Rad to Deg'
    arm_version = 1
    arm_section = 'angle'

    def init(self, context):
        super(RadToDegNode, self).init(context)
        self.add_input('ArmFloatSocket', 'Radians')

        self.add_output('ArmFloatSocket', 'Degrees')
