from arm.logicnode.arm_nodes import *

class ArrayFilterNode(ArmLogicTreeNode):
    """Returns an array with the filtered items of the given array."""
    bl_idname = 'LNArrayFilterNode'
    bl_label = 'Array Filter'
    arm_version = 1

    def remove_extra_inputs(self, context):
        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])
        if self.property0 == 'Item Field':
            self.add_input('ArmStringSocket', 'Item Field')
        if self.property0 == 'Item Property':
            self.add_input('ArmStringSocket', 'Item Property')
        self.add_input('ArmDynamicSocket', 'Value')
        if self.property1 == 'Between':
            self.add_input('ArmDynamicSocket', 'Value')
    
    property0: HaxeEnumProperty(
    'property0',
    items = [('Item', 'Item', 'Array Item'),
             ('Item Field', 'Item Field', 'Object Item Field, ie: Name, Uid, Visible, Parent, Length, etc.'),
             ('Item Property', 'Item Property', 'Object Item Property')],
    name='', default='Item', update=remove_extra_inputs)
    
    property1: HaxeEnumProperty(
    'property1',
    items = [('Equal', 'Equal', 'Equal'),
             ('Not Equal', 'Not Equal', 'Not Equal'),        
             ('Greater', 'Greater', 'Greater'),
             ('Greater Equal', 'Greater Equal', 'Greater Equal'),
             ('Less', 'Less', 'Less'),
             ('Less Equal', 'Less Equal', 'Less Equal'),
             ('Between', 'Between', 'Input 1 Between Input 2 and Input 3 inclusive'),
             ('Contains', 'Contains', 'Contains'),
             ('Starts With', 'Starts With', 'Starts With'),
             ('Ends With', 'Ends With', 'Ends With')],
    name='', default='Equal', update=remove_extra_inputs)

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketArray', 'Array')
        
    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')
