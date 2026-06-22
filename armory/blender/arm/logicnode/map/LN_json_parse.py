from arm.logicnode.arm_nodes import *


class ParseJsonNode(ArmLogicTreeNode):
    """Parse a JSON String to Haxe object.

    @input JSON: JSON string.

    @output Value: Parsed value.
    """

    bl_idname = 'LNParseJsonNode'
    bl_label = 'Parse JSON'
    arm_version = 1

    def init(self, context):
        self.add_input('ArmStringSocket', 'JSON')
        self.add_output('ArmDynamicSocket', 'Value')
