from arm.logicnode.arm_nodes import *

class RotateObjectNode(ArmLogicTreeNode):
    """Rotates the given object."""
    bl_idname = 'LNRotateObjectNode'
    bl_label = 'Rotate Object'
    arm_section = 'rotation'
    arm_version = 1

    def init(self, context):
        super().init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketRotation', 'Rotation')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    property0: EnumProperty(
        items = [('Local', 'Local F.O.R.', 'Frame of reference oriented with the object'),
                 ('Global', 'Global/Parent F.O.R.', 'Frame of reference oriented with the object\'s parent or the world')],
        name='', default='Local')
