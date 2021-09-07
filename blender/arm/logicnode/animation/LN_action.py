from arm.logicnode.arm_nodes import *

class AnimActionNode(ArmLogicTreeNode):
    """Samples a given action."""
    bl_idname = 'LNAnimActionNode'
    bl_label = 'Action'
    arm_version = 2

    property0: HaxeStringProperty('property0', name = 'Action ID', default = '')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimAction', 'Action')
        self.add_input('ArmBoolSocket', 'Is Looped')

        self.add_output('ArmNodeSocketAnimTree', 'Action')
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
    
    def draw_label(self) -> str:
        return f'{self.bl_label}: {self.property0}'
