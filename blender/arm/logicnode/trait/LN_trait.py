from arm.logicnode.arm_nodes import *

class TraitNode(ArmLogicTreeNode):
    """Stores the given trait as a variable. If the trait was not found or
    was not exported, an error is thrown ([more information](https://github.com/armory3d/armory/wiki/troubleshooting#trait-not-exported)).
    """
    bl_idname = 'LNTraitNode'
    bl_label = 'Trait'
    arm_version = 1

    property0: StringProperty(name='', default='')

    def init(self, context):
        super(TraitNode, self).init(context)
        self.add_output('NodeSocketShader', 'Trait', is_var=True)

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
