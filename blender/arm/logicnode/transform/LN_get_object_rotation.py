from arm.logicnode.arm_nodes import *

class GetRotationNode(ArmLogicTreeNode):
    """Returns the current rotation of the given object."""
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Object Rotation'
    arm_section = 'rotation'
    arm_version = 1

    def init(self, context):
        super(GetRotationNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketRotation', 'Rotation')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    property0: EnumProperty(
        items = [('Local', 'Local', 'Local'),
                 ('Global', 'Global', 'Global')],
        name='', default='Local')
