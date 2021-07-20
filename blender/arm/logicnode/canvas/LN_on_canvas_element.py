from arm.logicnode.arm_nodes import *

class OnCanvasElementNode(ArmLogicTreeNode):
    """Activates the output whether an action over the given UI element is done."""
    bl_idname = 'LNOnCanvasElementNode'
    bl_label = 'On Canvas Element'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items=[('click', 'Click', 'Listen to mouse clicks'),
               ('hover', 'Hover', 'Listen to mouse hover')],
        name='Listen to', default='click')
    property1: HaxeEnumProperty(
        'property1',
        items=[('started', 'Started', 'Started'),
               ('down', 'Down', 'Down'),
               ('released', 'Released', 'Released')],
        name='Status', default='started')
    property2: HaxeEnumProperty(
        'property2',
        items=[('left', 'Left', 'Left mouse button'),
               ('middle', 'Middle', 'Middle mouse button'),
               ('right', 'Right', 'Right mouse button')],
        name='Mouse Button', default='left')

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Element')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

        if self.property0 == "click":
            layout.prop(self, 'property1')
            layout.prop(self, 'property2')
