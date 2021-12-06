from arm.logicnode.arm_nodes import *

class OneShotActionNode(ArmLogicTreeNode):
    """Introduce one loop of animation in the current tree."""
    bl_idname = 'LNOneShotActionNode'
    bl_label = 'One Shot Action'
    arm_version = 1

    property0: HaxeStringProperty('property0', name = 'Action ID', default = '')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketAnimTree', 'Main Action')
        self.add_input('ArmNodeSocketAnimAction', 'One Shot')
        self.add_input('ArmBoolSocket', 'Restart', default_value = True)
        self.add_input('ArmFloatSocket', 'Blend In Time', default_value = 1.0)
        self.add_input('ArmFloatSocket', 'Blend Out Time', default_value = 1.0)
        self.add_input('ArmIntSocket', 'Bone Group', default_value = -1)

        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('ArmNodeSocketAnimTree', 'Result')
        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')