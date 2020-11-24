from arm.logicnode.arm_nodes import *

class ContainsStringNode(ArmLogicTreeNode):
    """Returns whether the given string contains a given part."""
    bl_idname = 'LNContainsStringNode'
    bl_label = 'String Contains'
    arm_version = 1
    property0: EnumProperty(
        items = [('Contains', 'Contains', 'Contains'),
                 ('Starts With', 'Starts With', 'Starts With'),
                 ('Ends With', 'Ends With', 'Ends With'),
                 ],
        name='', default='Contains')

    def init(self, context):
        super(ContainsStringNode, self).init(context)
        self.add_input('NodeSocketString', 'String')
        self.add_input('NodeSocketString', 'Find')

        self.add_output('NodeSocketBool', 'Contains')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
