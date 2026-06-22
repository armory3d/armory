from arm.logicnode.arm_nodes import *

class GetWorldOrientationNode(ArmLogicTreeNode):
    """Returns the world orientation of the given object."""
    bl_idname = 'LNGetWorldOrientationNode'
    bl_label = 'Get World Orientation'
    arm_section = 'rotation'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('Right', 'Right', 'The object right (X) direction'),
                 ('Look', 'Look', 'The object look (Y) direction'),
                 ('Up', 'Up', 'The object up (Z) direction')],
        name='', default='Look')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmVectorSocket', 'Vector')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
