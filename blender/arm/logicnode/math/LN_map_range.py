from arm.logicnode.arm_nodes import *

class MapRangeNode(ArmLogicTreeNode):
    """Converts the value between the given range to another range."""
    bl_idname = 'LNMapRangeNode'
    bl_label = 'Map Range'
    arm_version = 1

    def init(self, context):
        super(MapRangeNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Value', default_value=1.0)
        self.add_input('NodeSocketFloat', 'From Min')
        self.add_input('NodeSocketFloat', 'From Max', default_value=1.0)
        self.add_input('NodeSocketFloat', 'To Min')
        self.add_input('NodeSocketFloat', 'To Max', default_value=1.0)
        self.add_output('NodeSocketFloat', 'Result')
