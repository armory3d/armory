from arm.logicnode.arm_nodes import *

class CaseStringNode(ArmLogicTreeNode):
    """Converts strings's case node"""
    bl_idname = 'LNCaseStringNode'
    bl_label = 'Case String'
    arm_version = 1
    property0: EnumProperty(
        items = [('Upper Case', 'Upper Case', 'Upper Case'),
                 ('Lower Case', 'Lower Case', 'Lower Case'),
                 ],
        name='', default='Upper Case')

    def init(self, context):
        super(CaseStringNode, self).init(context)
        self.add_input('NodeSocketString', 'String In')
        self.add_output('NodeSocketString', 'String Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(CaseStringNode, category=PKG_AS_CATEGORY)
