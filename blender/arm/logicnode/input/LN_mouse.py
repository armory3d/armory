from arm.logicnode.arm_nodes import *


class MouseNode(ArmLogicTreeNode):
    """Activates the output on the given mouse event."""
    bl_idname = 'LNMergedMouseNode'
    bl_label = 'Mouse'
    arm_section = 'mouse'
    arm_version = 2

    property0: HaxeEnumProperty(
        'property0',
        items = [('started', 'Started', 'The mouse button begins to be pressed'),
                 ('down', 'Down', 'The mouse button is pressed'),
                 ('released', 'Released', 'The mouse button stops being pressed'),
                 ('moved', 'Moved', 'Moved')],
        name='', default='down')
    property1: HaxeEnumProperty(
        'property1',
        items = [('left', 'Left', 'Left mouse button'),
                 ('middle', 'Middle', 'Middle mouse button'),
                 ('right', 'Right', 'Right mouse button'),
                 ('side1', 'Side 1', 'Side 1 mouse button'),
                 ('side2', 'Side 2', 'Side 2 mouse button')],
        name='', default='left')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property1}'

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
