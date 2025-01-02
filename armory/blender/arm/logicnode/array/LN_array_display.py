from arm.logicnode.arm_nodes import *

class ArrayDisplayNode(ArmLogicTreeNode):
    """Returns the display of the given array."""
    bl_idname = 'LNArrayDisplayNode'
    bl_label = 'Array Display'
    arm_version = 1
    
    def remove_extra_inputs(self, context):
        while len(self.inputs) > 2:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Item Field':
            self.add_input('ArmStringSocket', 'Item Field')
        if self.property0 == 'Item Property':
            self.add_input('ArmStringSocket', 'Item Property')
    
    property0: HaxeEnumProperty(
    'property0',
    items = [('Item', 'Item', 'Array Item'),
             ('Item Field', 'Item Field', 'Object Item Field, ie: name, uid, visible, parent, length, etc.'),
             ('Item Property', 'Item Property', 'Object Item Property')],
    name='', default='Item', update=remove_extra_inputs)
    
    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmStringSocket', 'Separator')

        self.add_output('ArmStringSocket', 'Items')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')