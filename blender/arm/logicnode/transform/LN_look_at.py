from arm.logicnode.arm_nodes import *

class LookAtNode(ArmLogicTreeNode):
    """Converts the two given coordinates to a quaternion rotation."""
    bl_idname = 'LNLookAtNode'
    bl_label = 'Look At'
    arm_section = 'rotation'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('X', ' X', 'X'),
                 ('-X', '-X', '-X'),
                 ('Y', ' Y', 'Y'),
                 ('-Y', '-Y', '-Y'),
                 ('Z', ' Z', 'Z'),
                 ('-Z', '-Z', '-Z')],
        name='With', default='Z')

    def init(self, context):
        super(LookAtNode, self).init(context)
        self.add_input('NodeSocketVector', 'From Location')
        self.add_input('NodeSocketVector', 'To Location')

        self.add_output('NodeSocketVector', 'Rotation')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
