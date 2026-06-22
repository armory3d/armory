from arm.logicnode.arm_nodes import *

class ExpressionNode(ArmLogicTreeNode):
    """Evaluates a Haxe expression and returns its output.

    @output Result: the result of the expression."""
    bl_idname = 'LNExpressionNode'
    bl_label = 'Expression'
    arm_version = 1
    arm_section = 'haxe'

    property0: HaxeStringProperty('property0', name='', default='')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
