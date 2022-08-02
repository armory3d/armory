from arm.logicnode.arm_nodes import *

class ContainsStringNode(ArmLogicTreeNode):
    """Returns whether the given string contains a given part."""
    bl_idname = 'LNContainsStringNode'
    bl_label = 'String Contains'
    arm_version = 1
    property0: HaxeEnumProperty(
        'property0',
        items = [('Contains', 'Contains', 'Contains'),
                 ('Starts With', 'Starts With', 'Starts With'),
                 ('Ends With', 'Ends With', 'Ends With'),
                 ],
        name='', default='Contains')

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmStringSocket', 'Find')

        self.add_output('ArmBoolSocket', 'Contains')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
