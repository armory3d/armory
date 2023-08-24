from arm.logicnode.arm_nodes import *


class TraitNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given trait as a variable. If the trait was not found or
    was not exported, an error is thrown ([more information](https://github.com/armory3d/armory/wiki/troubleshooting#trait-not-exported)).
    """
    bl_idname = 'LNTraitNode'
    bl_label = 'Trait'
    arm_version = 1

    property0: HaxeStringProperty('property0', name='', default='')

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Trait', is_var=True)

    def draw_content(self, context, layout):
        layout.prop(self, 'property0')

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.property0 = master_node.property0
