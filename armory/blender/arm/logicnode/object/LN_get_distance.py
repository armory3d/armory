from arm.logicnode.arm_nodes import *

class GetDistanceNode(ArmLogicTreeNode):
    """Returns the euclidian distance between the two given objects.

    @see For distance between two locations, use the `Distance` operator
        in the *[`Vector Math`](#vector-math)* node."""
    bl_idname = 'LNGetDistanceNode'
    bl_label = 'Get Distance'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmFloatSocket', 'Distance')
