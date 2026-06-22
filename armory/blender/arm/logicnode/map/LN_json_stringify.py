from arm.logicnode.arm_nodes import *


class JsonStringifyNode(ArmLogicTreeNode):
    """Convert a Haxe object to JSON String.

    @input Value: Value to convert.

    @output String: JSON String.
    """

    bl_idname = 'LNJsonStringifyNode'
    bl_label = 'JSON Stringify'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmDynamicSocket', 'Value')
        self.add_output('ArmStringSocket', 'JSON')