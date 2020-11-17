from arm.logicnode.arm_nodes import *

class SetActivationStateNode(ArmLogicTreeNode):
    """Sets the rigid body simulation state of the given object."""
    bl_idname = 'LNSetActivationStateNode'
    bl_label = 'Set RB Activation State'
    bl_icon = 'NONE'
    arm_version = 1

    property0: EnumProperty(
        items = [('Inactive', 'Inactive', 'The rigid body simulation is desactivated'),
                 ('Active', 'Active', 'The rigid body simulation is activated'),
                 ('Always Active', 'Always Active', 'The rigid body simulation is never desactivated'),
                 ('Always Inactive', 'Always Inactive', 'The rigid body simulation is never activated'),
                 ],
        name='', default='Inactive')

    def init(self, context):
        super(SetActivationStateNode, self).init(context)
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'RB')

        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
