from arm.logicnode.arm_nodes import *


class ScreenToWorldSpaceNode(ArmLogicTreeNode):
    """Transforms the given screen coordinates into World coordinates.
    
    @input Screen X: screen x position.
    @input Screen Y: screen y position.
    @input Distance at: distance from camera to the result vector position.
    Try between 0 and 1.

    @output Screen At: result vector position.
    @output Screen Word: origin position of the ray emitted from camera.
    @output Screen Direction: ray direction.
    """

    bl_idname = 'LNScreenToWorldSpaceNode'
    bl_label = 'Screen to World Space'
    arm_section = 'matrix'
    arm_version = 2
    max_outputs = 9

    property0: HaxeBoolProperty('property0', name='Separator Out', default=False)

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Screen X')
        self.add_input('ArmIntSocket', 'Screen Y')
        self.add_input('ArmFloatSocket', 'Distance at', default_value = 0.1)

        self.add_output('ArmVectorSocket', 'At')
        self.add_output('ArmVectorSocket', 'Origin')
        self.add_output('ArmVectorSocket', 'Direction')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')  # Separator Out
        if self.property0:
            if len(self.outputs) < self.max_outputs:
                self.outputs.remove(self.outputs.values()[-1])  # Direction vector
                self.add_output('ArmFloatSocket', 'X')  # Origin X
                self.add_output('ArmFloatSocket', 'Y')  # Origin Y
                self.add_output('ArmFloatSocket', 'Z')  # Origin Z
                self.add_output('ArmVectorSocket', 'Direction')  # Vector
                self.add_output('ArmFloatSocket', 'X')  # Direction X
                self.add_output('ArmFloatSocket', 'Y')  # Direction Y
                self.add_output('ArmFloatSocket', 'Z')  # Direction Z
        else:
            if len(self.outputs) == self.max_outputs:
                self.outputs.remove(self.outputs.values()[-1])  # Z
                self.outputs.remove(self.outputs.values()[-1])  # Y
                self.outputs.remove(self.outputs.values()[-1])  # X
                self.outputs.remove(self.outputs.values()[-1])  # Direction
                self.outputs.remove(self.outputs.values()[-1])  # Z
                self.outputs.remove(self.outputs.values()[-1])  # Y
                self.outputs.remove(self.outputs.values()[-1])  # X
                self.add_output('ArmVectorSocket', 'Direction')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)