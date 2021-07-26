from arm.logicnode.arm_nodes import *

class MapRangeNode(ArmLogicTreeNode):
    """Converts the given value from a range to another range.

    @seeNode Clamp
    """
    bl_idname = 'LNMapRangeNode'
    bl_label = 'Map Range'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Value', default_value=1.0)
        self.add_input('ArmFloatSocket', 'From Min')
        self.add_input('ArmFloatSocket', 'From Max', default_value=1.0)
        self.add_input('ArmFloatSocket', 'To Min')
        self.add_input('ArmFloatSocket', 'To Max', default_value=1.0)

        self.add_output('ArmFloatSocket', 'Result')
