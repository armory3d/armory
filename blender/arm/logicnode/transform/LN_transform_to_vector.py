from arm.logicnode.arm_nodes import *

class VectorFromTransformNode(ArmLogicTreeNode):
    """Returns vector from the given transform."""
    bl_idname = 'LNVectorFromTransformNode'
    bl_label = 'Transform to Vector'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmVectorSocket', 'Vector')
        self.add_output('ArmVectorSocket', 'Quaternion XYZ')
        self.add_output('ArmFloatSocket', 'Quaternion W')

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

    property0: HaxeEnumProperty(
        'property0',
        items = [('Right', 'Right', 'The transform right (X) direction'),
                 ('Look', 'Look', 'The transform look (Y) direction'),
                 ('Up', 'Up', 'The transform up (Z) direction'),
                 ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='Look',
        update=on_property_update)
