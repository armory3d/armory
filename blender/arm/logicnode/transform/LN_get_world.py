from arm.logicnode.arm_nodes import *

class GetWorldNode(ArmLogicTreeNode):
    """Get world node"""
    bl_idname = 'LNGetWorldNode'
    bl_label = 'Get World'
    arm_version = 1

    property0: EnumProperty(
        items = [('Right', 'Right', 'Right'),
                 ('Look', 'Look', 'Look'),
                 ('Up', 'Up', 'Up')],
        name='', default='Look')

    def init(self, context):
        super(GetWorldNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Vector')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(GetWorldNode, category=PKG_AS_CATEGORY, section='rotation')
