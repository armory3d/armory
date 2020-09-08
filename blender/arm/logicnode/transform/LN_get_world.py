from arm.logicnode.arm_nodes import *

class GetWorldNode(ArmLogicTreeNode):
    """Get world node"""
    bl_idname = 'LNGetWorldNode'
    bl_label = 'Get World'

    property0: EnumProperty(
        items = [('right', 'right', 'right'),
                 ('look', 'look', 'look'),
                 ('up', 'up', 'up')],
        name='', default='right')

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Vector')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(GetWorldNode, category=MODULE_AS_CATEGORY, section='rotation')
