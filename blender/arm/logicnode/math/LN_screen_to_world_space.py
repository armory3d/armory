from arm.logicnode.arm_nodes import *

class ScreenToWorldSpaceNode(ArmLogicTreeNode):
    """Transforms the given screen coordinates into world coordinates."""
    bl_idname = 'LNScreenToWorldSpaceNode'
    bl_label = 'Screen to World Space'
    node_index: StringProperty(name='Node Index', default='')
    arm_section = 'matrix'
    arm_version = 1
    min_outputs = 2
    max_outputs = 8

    # Separator
    @property
    def property0(self):
        return True if self.property0_ else False

    property0_: BoolProperty(name='Separator Out', default=False)

    def init(self, context):
        super(ScreenToWorldSpaceNode, self).init(context)
        self.add_input('NodeSocketInt', 'Screen X')
        self.add_input('NodeSocketInt', 'Screen Y')

        self.add_output('NodeSocketVector', 'World')
        self.add_output('NodeSocketVector', 'Direction')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0_') # Separator Out
        if self.property0_:
            if len(self.outputs) < self.max_outputs:
                self.outputs.remove(self.outputs.values()[-1]) # Direction vector
                self.add_output('NodeSocketFloat', 'X') # World X
                self.add_output('NodeSocketFloat', 'Y') # World Y
                self.add_output('NodeSocketFloat', 'Z') # World Z
                self.add_output('NodeSocketVector', 'Direction') # Vector
                self.add_output('NodeSocketFloat', 'X') # Direction X
                self.add_output('NodeSocketFloat', 'Y') # Direction Y
                self.add_output('NodeSocketFloat', 'Z') # Direction Z
        else:
            if len(self.outputs) == self.max_outputs:
                self.outputs.remove(self.outputs.values()[-1]) # Z
                self.outputs.remove(self.outputs.values()[-1]) # Y
                self.outputs.remove(self.outputs.values()[-1]) # X
                self.outputs.remove(self.outputs.values()[-1]) # Direction
                self.outputs.remove(self.outputs.values()[-1]) # Z
                self.outputs.remove(self.outputs.values()[-1]) # Y
                self.outputs.remove(self.outputs.values()[-1]) # X
                self.add_output('NodeSocketVector', 'Direction')
