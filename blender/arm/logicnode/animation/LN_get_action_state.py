from arm.logicnode.arm_nodes import *

class AnimationStateNode(ArmLogicTreeNode):
    """Returns the information about the current action of the given object."""
    bl_idname = 'LNAnimationStateNode'
    bl_label = 'Get Action State'
    arm_version = 2

    property0: HaxeStringProperty('property0', name='Action ID', default='')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')        

        self.add_output('ArmStringSocket', 'Action Name')
        self.add_output('ArmIntSocket', 'Frame')
        self.add_output('ArmBoolSocket', 'Is Paused')
        self.add_output('ArmNodeSocketAction', 'On Complete')
    
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
