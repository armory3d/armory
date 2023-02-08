from arm.logicnode.arm_nodes import *

class SetCameraStartEndNode(ArmLogicTreeNode):
    """Sets the Start & End of the given camera.

    @seeNode Get Camera Start & End"""
    bl_idname = 'LNSetCameraStartEndNode'
    bl_label = 'Set Camera Start End'
    arm_version = 1
    
    def remove_extra_inputs(self, context):
        while len(self.inputs) > 2:
                self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Start':
            self.add_input('ArmFloatSocket', 'Start')
        if self.property0 == 'End':
            self.add_input('ArmFloatSocket', 'End')
        if self.property0 == 'Start&End':
            self.add_input('ArmFloatSocket', 'Start')
            self.add_input('ArmFloatSocket', 'End')
       
    property0: HaxeEnumProperty(
    'property0',
    items = [('Start&End', 'Start&End', 'Start&End'),
             ('Start', 'Start', 'Start'),
             ('End', 'End', 'End')],
    name='', default='Start&End', update=remove_extra_inputs)
    

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmFloatSocket', 'Start')
        self.add_input('ArmFloatSocket', 'End')

        self.add_output('ArmNodeSocketAction', 'Out')
        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
