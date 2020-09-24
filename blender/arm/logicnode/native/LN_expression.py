from arm.logicnode.arm_nodes import *

class ExpressionNode(ArmLogicTreeNode):
    """Use to get the value of an defined expression."""
    bl_idname = 'LNExpressionNode'
    bl_label = 'Expression'
    arm_version = 1

    property0: StringProperty(name='', default='')

    def init(self, context):
        super(ExpressionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketShader', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(ExpressionNode, category=PKG_AS_CATEGORY, section='haxe')
