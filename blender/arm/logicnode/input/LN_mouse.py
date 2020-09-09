from arm.logicnode.arm_nodes import *

class MouseNode(ArmLogicTreeNode):
    """Mouse node"""
    bl_idname = 'LNMergedMouseNode'
    bl_label = 'Mouse'
    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Down')
    property1: EnumProperty(
        items = [('left', 'left', 'left'),
                 ('right', 'right', 'right'),
                 ('middle', 'middle', 'middle')],
        name='', default='left')

    def init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketBool', 'State')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(MouseNode, category=PKG_AS_CATEGORY, section='mouse')
