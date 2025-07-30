from arm.logicnode.arm_nodes import *


class FunctionOutputNode(ArmLogicTreeNode):
    """Sets the return value for the given function.

    @seeNode Function"""
    bl_idname = 'LNFunctionOutputNode'
    bl_label = 'Function Output'
    arm_section = 'function'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Value')

    function_name: StringProperty(name="Name")

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, 'function_name')
