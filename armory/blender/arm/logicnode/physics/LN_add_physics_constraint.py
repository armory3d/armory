from arm.logicnode.arm_nodes import *

class AddPhysicsConstraintNode(ArmLogicTreeNode):
    """
    Add a physics constraint to constrain two rigid bodies if not already present.

    @option Fixed: No fredom of movement. Relative positions and rotations of rigid bodies are fixed

    @option Point: Both rigid bodies are constrained at the pivot object.

    @option Hinge: Constrained objects can move only along angular Z axis of the pivot object.

    @option Slider: Constrained objects can move only along linear X axis of the pivot object.

    @option Piston: Constrained objects can move only and rotate along X axis of the pivot object.

    @option GenericSpring: Fully custimizable generic 6 degree of freedom constraint with optional springs. All liner and angular axes can be constrained
    along with spring options. Use `Physics Constraint Node` to set a combination of constraints and springs.

    @seeNode Physics Constraint

    @input Pivot object: The object to which the physics constraint traint is applied. This object will not be affected by the constraint
    but is necessary to specify the constraint axes and location. Hence, the pivot object need not be a rigid body. Typically an `Empty`
    object may be used. Each pivot object can have only one constraint trait applied. Moving/rotating/parenting the pivot object after the constraint
    is applied has no effect. However, removig the pivot object removes the constraint and `RB 1` and `RB 2` are no longer constrained.

    @input RB 1: The first rigid body to be constrained. Must be a rigid body. This object can be constrained by more than one constraint.

    @input RB 2: The second rigid body to be constrained. Must be a rigid body. This object can be constrained by more than one constraint.

    @input Disable Collisions: Disable collisions between `RB 1` and `RB 2`

    @input Breakable: Constraint can break if stress on the constraint is more than the set threshold. Disable this option to disable breaking.

    @input Breaking threshold: Stress on the constraint above which the constraint breaks. Depends on the mass, velocity of rigid bodies and type of constraint.

    @input Limit Lower: Lower limit of the consraint in that particular axis

    @input Limit Upper: Upper limit of the constraint in that particular axis. (`lower limit` = `upper limit`) --> Fully constrained. (`lower limit` < `upper limit`) --> Partially constrained
    (`lower limit` > `upper limit`) --> Full freedom.

    @input Angular limits: Limits to constarin rotation. Specified in degrees. Range (-360 to +360)

    @input Add Constarint: Option to add custom constraint to `Generic Spring` type.
    """


    bl_idname = 'LNAddPhysicsConstraintNode'
    bl_label = 'Add Physics Constraint'
    arm_section = 'add'
    arm_version = 1

    @staticmethod
    def get_enum_id_value(obj, prop_name, value):
        return obj.bl_rna.properties[prop_name].enum_items[value].identifier

    @staticmethod
    def get_count_in(type_name):
        return {
            'Fixed': 0,
            'Point': 1,
            'Hinge': 2,
            'Slider': 3,
            'Piston': 4,
            'Generic Spring': 5
        }.get(type_name, 0)

    def get_enum(self):
        return self.get('property0', 0)

    def set_enum(self, value):
        # Checking the selection of another type
        select_current = self.get_enum_id_value(self, 'property0', value)
        select_prev = self.property0

        #Check if a different type is selected
        if select_prev != select_current:
            print('New value selected')
            # Arguements for type Fixed
            if (self.get_count_in(select_current) == 0):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])

            # Arguements for type Point
            if (self.get_count_in(select_current) == 1):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])

            #Arguements for type Hinge
            if (self.get_count_in(select_current) == 2):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #Z ang limits
                self.add_input('ArmBoolSocket', 'Z angle')
                self.add_input('ArmFloatSocket', 'Z ang lower', -45.0)
                self.add_input('ArmFloatSocket', 'Z ang upper', 45.0)

            #Arguements for type Slider
            if (self.get_count_in(select_current) == 3):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #X lin limits
                self.add_input('ArmBoolSocket', 'X linear')
                self.add_input('ArmFloatSocket', 'X lin lower')
                self.add_input('ArmFloatSocket', 'X lin upper')

            #Arguements for type Piston
            if (self.get_count_in(select_current) == 4):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])
                #X lin limits
                self.add_input('ArmBoolSocket', 'X linear')
                self.add_input('ArmFloatSocket', 'X lin lower')
                self.add_input('ArmFloatSocket', 'X lin upper')
                #X ang limits
                self.add_input('ArmBoolSocket', 'X angle')
                self.add_input('ArmFloatSocket', 'X ang lower', -45.0)
                self.add_input('ArmFloatSocket', 'X ang upper', 45.0)

            #Arguements for type GenericSpring
            if (self.get_count_in(select_current) == 5):
                while (len(self.inputs) > 7):
                    self.inputs.remove(self.inputs.values()[-1])

        self['property0'] = value

    property0: HaxeEnumProperty(
        'property0',
        items = [('Fixed', 'Fixed', 'Fixed'),
                 ('Point', 'Point', 'Point'),
                 ('Hinge', 'Hinge', 'Hinge'),
                 ('Slider', 'Slider', 'Slider'),
                 ('Piston', 'Piston', 'Piston'),
                 ('Generic Spring', 'Generic Spring', 'Generic Spring')],
        name='Type', default='Fixed', set=set_enum, get=get_enum)

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Pivot Object')
        self.add_input('ArmNodeSocketObject', 'RB 1')
        self.add_input('ArmNodeSocketObject', 'RB 2')
        self.add_input('ArmBoolSocket', 'Disable Collissions')
        self.add_input('ArmBoolSocket', 'Breakable')
        self.add_input('ArmFloatSocket', 'Breaking Threshold')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

        #GenericSpring:
        if (self.get_count_in(self.property0) == 5):
            grid0 = layout.grid_flow(row_major=True, columns=1, align=True)
            grid0.label(text="Possible Constraints:")
            grid0.label(text="Linear [X, Y, Z]")
            grid0.label(text="Angular [X, Y, Z]")
            grid0.label(text="Spring Linear [X, Y, Z]")
            grid0.label(text="Spring Angular [X, Y, Z]")
            row = layout.row(align=True)
            column = row.column(align=True)
            op = column.operator('arm.node_add_input', text='Add Constraint', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            op.socket_type = 'ArmDynamicSocket'
            op.name_format = 'Constraint {0}'.format(len(self.inputs) - 6)
            column1 = row.column(align=True)
            op = column1.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op.node_index = str(id(self))
            #Static inputs
            if len(self.inputs) < 8:
                column1.enabled = False
            #Max Possible inputs
            if len(self.inputs) > 18:
                column.enabled = False

