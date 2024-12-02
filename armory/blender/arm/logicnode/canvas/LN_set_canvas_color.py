from arm.logicnode.arm_nodes import *


class CanvasSetColorNode(ArmLogicTreeNode):
    """Sets the selected color attribute of the given UI element.

    This node does not override theme colors, only colors of individual
    elements are affected.

    @input Element: The name of the canvas element whose color to set.
    @input Color: The color to set.

    @option Attribute: The color attribute to set by this node. Not all
        attributes work for all canvas element types. If in doubt, see
        [`CanvasScript.hx`](https://github.com/armory3d/armory/blob/main/Sources/armory/ui/Canvas.hx)
        for details.
    """
    bl_idname = 'LNCanvasSetColorNode'
    bl_label = 'Set Canvas Color'
    arm_section = 'elements_general'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items=[
            ('color', 'Color', 'Set the element\'s color attribute'),
            ('color_text', 'Text Color', 'Set the element\'s color_text attribute'),
            ('color_hover', 'Hover Color', 'Set the element\'s color_hover attribute'),
            ('color_press', 'Pressed Color', 'Set the element\'s color_press attribute'),
            ('color_progress', 'Progress Color', 'Set the element\'s color_progress attribute'),
        ],
        name='Attribute', default='color', description='The color attribute to set by this node')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Element')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0', text='')
