from arm.logicnode.arm_nodes import *

class AddRigidBodyNode(ArmLogicTreeNode):
    """Adds a rigid body to an object if not already present.

    @option Advanced: Shows optional advanced options for rigid body.

    @option Shape: Shape of the rigid body including Box, Sphere, Capsule, Cone, Cylinder, Convex Hull and Mesh

    @input Object: Object to which rigid body is added.

    @input Mass: Mass of the rigid body. Must be > 0.

    @input Active: Rigid body actively participates in the physics world and will be affected by collisions

    @input Animated: Rigid body follows animation and will affect other active non-animated rigid bodies.

    @input Trigger: Rigid body behaves as a trigger and detects collision. However, rigd body does not contribute to or receive collissions.

    @input Friction: Surface friction of the rigid body. Minimum value = 0, Preferred max value = 1.

    @input Bounciness: How elastic is the surface of the rigid body. Minimum value = 0, Preferred max value = 1.

    @input Continuous Collision Detection (CCD): Detects for collisions in between frames. Use only for very fast moving objects.

    @input Collision Margin: Enable an external margin for collision detection

    @input Margin: Length of the collision margin. Must be > 0.

    @input Linear Damping: Damping for linear translation. Recommended range 0 to 1.

    @input Angular Damping: Damping for angular translation. Recommended range 0 to 1.

    @input Angular Friction: Rolling or angular friction. Recommended range >= 0

    @input Use Deactivation: Deactive this rigid body when below the Linear and Angular velocity threshold. Enable to improve performance.

    @input Linear Velocity Threshold: Velocity below which decativation occurs if enabled.

    @input Angular Velocity Threshold: Velocity below which decativation occurs if enabled.

    @input Collision Group: A set of rigid bodies that can interact with each other

    @input Collision Mask: Bitmask to filter collisions. Collision can occur between two rigid bodies if they have atleast one bit in common.

    @output Rigid body: Object to which rigid body was added.

    @output Out: activated after rigid body is added.
    """

    bl_idname = 'LNAddRigidBodyNode'
    bl_label = 'Add Rigid Body'
    arm_version = 2

    NUM_STATIC_INS = 9

    def update_advanced(self, context):
        """This is a helper method to allow declaring the `advanced`
        property before the update_sockets() method. It's not required
        but then you would need to move the declaration of `advanced`
        further down."""
        self.update_sockets(context)

    property1: HaxeBoolProperty(
        'property1',
        name="Advanced",
        description="Show advanced options",
        default=False,
        update=update_advanced
    )

    property0: HaxeEnumProperty(
        'property0',
        items = [('Box', 'Box', 'Box'),
                 ('Sphere', 'Sphere', 'Sphere'),
                 ('Capsule', 'Capsule', 'Capsule'),
                 ('Cone', 'Cone', 'Cone'),
                 ('Cylinder', 'Cylinder', 'Cylinder'),
                 ('Convex Hull', 'Convex Hull', 'Convex Hull'),
                 ('Mesh', 'Mesh', 'Mesh')],
        name='Shape', default='Box')

    def arm_init(self, context):

        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmFloatSocket', 'Mass', 1.0)
        self.add_input('ArmBoolSocket', 'Active', True)
        self.add_input('ArmBoolSocket', 'Animated', False)
        self.add_input('ArmBoolSocket', 'Trigger', False)
        self.add_input('ArmFloatSocket', 'Friction', 0.5)
        self.add_input('ArmFloatSocket', 'Bounciness', 0.0)
        self.add_input('ArmBoolSocket', 'Continuous Collision Detection', False)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketObject', 'Rigid body')

        self.update_sockets(context)

    def update_sockets(self, context):
        # It's bad to remove from a list during iteration so we use
        # this helper list here
        remove_list = []

        # Remove dynamically placed input sockets
        for i in range(AddRigidBodyNode.NUM_STATIC_INS, len(self.inputs)):
            remove_list.append(self.inputs[i])
        for i in remove_list:
            self.inputs.remove(i)

        # Add dynamic input sockets
        if self.property1:
            self.add_input('ArmBoolSocket', 'Collision Margin', False)
            self.add_input('ArmFloatSocket', 'Margin', 0.04)
            self.add_input('ArmFloatSocket', 'Linear Damping', 0.04)
            self.add_input('ArmFloatSocket', 'Angular Damping', 0.1)
            self.add_input('ArmFloatSocket', 'Angular Friction', 0.1)
            self.add_input('ArmBoolSocket', 'Use Deacivation')
            self.add_input('ArmFloatSocket', 'Linear Velocity Threshold', 0.4)
            self.add_input('ArmFloatSocket', 'Angular Velocity Threshold', 0.5)
            self.add_input('ArmIntSocket', 'Collision Group', 1)
            self.add_input('ArmIntSocket', 'Collision Mask', 1)


    def draw_buttons(self, context, layout):
        layout.prop(self, "property1")
        layout.prop(self, 'property0')
    
    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        in_socket_mapping={0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8}
        if self.property1:
            in_socket_mapping.update({9:9, 10:10, 11:11, 12:12, 13:14, 14:15, 15:16, 16:17, 17:18})

        return NodeReplacement(
            'LNAddRigidBodyNode', self.arm_version, 'LNAddRigidBodyNode', 2,
            in_socket_mapping=in_socket_mapping,
            out_socket_mapping={0:0, 1:1},
            property_mapping={'property0':'property0', 'property1':'property1'})
