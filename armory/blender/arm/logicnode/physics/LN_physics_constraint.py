from arm.logicnode.arm_nodes import *


class PhysicsConstraintNode(ArmLogicTreeNode):
    """
    Custom physics constraint to add to `Add Physics Constarint` node.

    @option Linear/Angualr: Select if constrint is applied along linear or angular axis.

    @option Axis: Local axis of the pivot object along which the constraint is applied.

    @option Spring: Constraint is a Spring along the selected axis.

    @input Limit Lower: Lower limit of the consraint in that particular axis

    @input Limit Upper: Upper limit of the constraint in that particular axis. (`lower limit` = `upper limit`) --> Fully constrained. (`lower limit` < `upper limit`) --> Partially constrained
    (`lower limit` > `upper limit`) --> Full freedom.

    @seeNode Add Physics Constraint
    """

    bl_idname = 'LNPhysicsConstraintNode'
    bl_label = 'Physics Constraint'
    arm_section = 'add'
    arm_version = 1

    def update_spring(self, context):
        self.update_sockets(context)

    property0: HaxeEnumProperty(
        'property0',
        items=[('Linear', 'Linear', 'Linear'),
               ('Angular', 'Angular', 'Angular')],
        name='Type', default='Linear')

    property1: HaxeEnumProperty(
        'property1',
        items=[('X', 'X', 'X'),
               ('Y', 'Y', 'Y'),
               ('Z', 'Z', 'Z')],
        name='Axis', default='X')

    property2: HaxeBoolProperty(
        'property2',
        name="Spring",
        description="Is a spring constraint",
        default=False,
        update=update_spring
    )

    def __init__(self, *args, **kwargs):
        super(PhysicsConstraintNode, self).__init__(*args, **kwargs)

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Lower limit')
        self.add_input('ArmFloatSocket', 'Upper limit')
        self.add_output('ArmDynamicSocket', 'Constraint')

    def update_sockets(self, context):
        while len(self.inputs) > 0:
            self.inputs.remove(self.inputs.values()[-1])

        # Add dynamic input sockets
        if self.property2:
            self.add_input('ArmFloatSocket', 'Stiffness', 10.0)
            self.add_input('ArmFloatSocket', 'Damping', 0.5)
        else:
            self.add_input('ArmFloatSocket', 'Lower limit')
            self.add_input('ArmFloatSocket', 'Upper limit')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
        layout.prop(self, 'property2')
