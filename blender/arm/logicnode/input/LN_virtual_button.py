from arm.logicnode.arm_nodes import *

class VirtualButtonNode(ArmLogicTreeNode):
    """Virtual button node"""
    bl_idname = 'LNMergedVirtualButtonNode'
    bl_label = 'Virtual Button'
    arm_version = 1
    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Started')
    property1: StringProperty(name='', default='button')

    def init(self, context):
        super(VirtualButtonNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(VirtualButtonNode, category=PKG_AS_CATEGORY, section='virtual')
