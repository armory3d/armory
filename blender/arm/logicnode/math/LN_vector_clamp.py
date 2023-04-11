from arm.logicnode.arm_nodes import *


class VectorClampToSizeNode(ArmLogicTreeNode):
    """Clamp the vector's value inside the given range and return the result as a new vector.

    @option Clamping Mode: Whether to clamp the length of the vector
        or the value of each individual component.
    """
    bl_idname = 'LNVectorClampToSizeNode'
    bl_label = 'Vector Clamp'
    arm_section = 'vector'
    arm_version = 2

    property0: HaxeEnumProperty(
        'property0',
        name='Clamping Mode', default='length',
        items=[
            ('length', 'Length', 'Clamp the length (magnitude) of the vector'),
            ('components', 'Components', 'Clamp the individual components of the vector'),
        ]
    )

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.label(text="Clamping Mode:")
        col.prop(self, 'property0', expand=True)

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Vector In', default_value=[0.0, 0.0, 0.0])
        self.add_input('ArmFloatSocket', 'Min')
        self.add_input('ArmFloatSocket', 'Max')

        self.add_output('ArmVectorSocket', 'Vector Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
