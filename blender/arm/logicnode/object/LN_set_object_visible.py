from arm.logicnode.arm_nodes import *

class SetVisibleNode(ArmLogicTreeNode):
    """Sets whether the given object is visible.

    @input Object: Object whose property to be set.

    @input Visible: Visibility.

    @input Children: Set the visibility of the children too. Visibility is set only to the immediate children.

    @input Recursive: If enabled, visibility of all the children in the tree is set. Ignored if `Children` is disabled.

    @seeNode Get Object Visible"""
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Object Visible'
    arm_section = 'props'
    arm_version = 2

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
        self.add_input('ArmBoolSocket', 'Recursive', default_value=False)

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)