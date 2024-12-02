from arm.logicnode.arm_nodes import *

class WorldToScreenSpaceNode(ArmLogicTreeNode):
    """Transforms the given world coordinates into screen coordinates,
    using the active camera or a selected camera."""
    bl_idname = 'LNWorldToScreenSpaceNode'
    bl_label = 'World to Screen Space'
    arm_section = 'matrix'
    arm_version = 2

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Selected Camera':
            self.add_input('ArmNodeSocketObject', 'Camera')

    property0: HaxeEnumProperty(
    'property0',
    items = [('Active Camera', 'Active Camera', 'Active Camera'),
             ('Selected Camera', 'Selected Camera', 'Selected Camera')],
    name='', default='Active Camera', update=remove_extra_inputs)

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'World')

        self.add_output('ArmVectorSocket', 'Screen')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
