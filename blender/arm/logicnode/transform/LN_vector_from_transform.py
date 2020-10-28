from arm.logicnode.arm_nodes import *

class VectorFromTransformNode(ArmLogicTreeNode):
    """Returns vector from the given transform."""
    bl_idname = 'LNVectorFromTransformNode'
    bl_label = 'Vector From Transform'
    arm_version = 1

    def init(self, context):
        super(VectorFromTransformNode, self).init(context)
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketVector', 'Quaternion XYZ')
        self.add_output('NodeSocketFloat', 'Quaternion W')

    def on_property_update(self, context):
        """called by the EnumProperty, used to update the node socket labels"""
        # note: the conditions on len(self.outputs) are take in account "old version" (pre-2020.9) nodes, which only have one output
        if self.property0 == "Quaternion":
            self.outputs[0].name = "Quaternion"
            if len(self.outputs) > 1:
                self.outputs[1].name = "Quaternion XYZ"
                self.outputs[2].name = "Quaternion W"
        else:
            self.outputs[0].name = "Vector"
            if len(self.outputs) > 1:
                self.outputs[1].name = "[quaternion only]"
                self.outputs[2].name = "[quaternion only]"

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    property0: EnumProperty(
        items = [('Up', 'Up', 'Up'),
                 ('Right', 'Right', 'Right'),
                 ('Look', 'Look', 'Look'),
                 ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='Look',
        update=on_property_update)
