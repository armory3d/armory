from arm.logicnode.arm_nodes import *

class TraitNode(ArmLogicTreeNode):
    """Trait node"""
    bl_idname = 'LNTraitNode'
    bl_label = 'Trait'

    property0: StringProperty(name='', default='')

    def init(self, context):
        self.add_output('NodeSocketShader', 'Trait', is_var=True)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(TraitNode, category=MODULE_AS_CATEGORY)
