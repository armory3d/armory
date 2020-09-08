from arm.logicnode.arm_nodes import *

class RotateObjectAroundAxisNode(ArmLogicTreeNode):
    """Rotate object around axis node"""
    bl_idname = 'LNRotateObjectAroundAxisNode'
    bl_label = 'Rotate Object Around Axis'
    bl_description = 'Rotate Object Around Axis (Depreciated: use "Rotate Object")'
    bl_icon = 'ERROR'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Axis', default_value=[0, 0, 1])
        self.add_input('NodeSocketFloat', 'Angle')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.label(text='Depreciated. Consider using "Rotate Object"')

add_node(RotateObjectAroundAxisNode, category=MODULE_AS_CATEGORY, section='rotation')
