from arm.logicnode.arm_nodes import *

class CaseStringNode(ArmLogicTreeNode):
    """Changes the given string case."""
    bl_idname = 'LNCaseStringNode'
    bl_label = 'String Case'
    arm_version = 1
    property0: HaxeEnumProperty(
        'property0',
        items = [('Upper Case', 'Upper Case', 'Upper Case'),
                 ('Lower Case', 'Lower Case', 'Lower Case'),
                 ],
        name='', default='Upper Case')

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'String In')

        self.add_output('ArmStringSocket', 'String Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
