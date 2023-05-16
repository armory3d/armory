from arm.logicnode.arm_nodes import *

class SetVisibleNode(ArmLogicTreeNode):
    """Sets whether the given object is visible.

    @seeNode Get Object Visible"""
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Object Visible'
    arm_section = 'props'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('object', 'Object', 'All object componenets visibility'),
                 ('mesh', 'Mesh', 'Mesh visibility only'),
                 ('shadow', 'Shadow', 'Shadow visibility only'),
                 ],
        name='', default='object')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Visible')
        self.add_input('ArmBoolSocket', 'Children', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
