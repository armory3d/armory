from arm.logicnode.arm_nodes import *

class LookAtNode(ArmLogicTreeNode):
    """Returns *a* rotation that makes something look away from X,Y or Z, and instead look in the 'from->to' direction"""
    bl_idname = 'LNLookAtNode'
    bl_label = 'Look At'
    arm_section = 'rotation'
    arm_version = 1

    property0: EnumProperty(
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

        self.add_output('ArmNodeSocketRotation', 'Rotation')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
