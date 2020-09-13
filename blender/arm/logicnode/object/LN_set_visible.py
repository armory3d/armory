from arm.logicnode.arm_nodes import *

class SetVisibleNode(ArmLogicTreeNode):
    """Set Visible node"""
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Visible'
    arm_version = 1

    property0: EnumProperty(
        items = [('Object', 'Object', 'Object'),
                 ('Mesh', 'Mesh', 'Mesh'),
                 ('Shadow', 'Shadow', 'Shadow'),
                 ],
        name='', default='Object')

    def init(self, context):
        super(SetVisibleNode, self).init(context)
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketBool', 'Visible')
        self.inputs.new('NodeSocketBool', 'Children')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(SetVisibleNode, category=PKG_AS_CATEGORY, section='props')
