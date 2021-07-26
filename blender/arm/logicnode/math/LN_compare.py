from arm.logicnode.arm_nodes import *

def remove_extra_inputs(self, context):
    if not any(p == self.property0 for p in ['Or', 'And']):
        while len(self.inputs) > self.min_inputs:
            self.inputs.remove(self.inputs[-1])

class CompareNode(ArmLogicTreeNode):
    """Compares values."""
    bl_idname = 'LNCompareNode'
    bl_label = 'Compare'
    arm_version = 1
    property0: HaxeEnumProperty(
        'property0',
        items = [('Equal', 'Equal', 'Equal'),
                 ('Almost Equal', 'Almost Equal', 'Almost Equal'),
                 ('Greater', 'Greater', 'Greater'),
                 ('Greater Equal', 'Greater Equal', 'Greater Equal'),
                 ('Less', 'Less', 'Less'),
                 ('Less Equal', 'Less Equal', 'Less Equal'),
                 ('Or', 'Or', 'Or'),
                 ('And', 'And', 'And')],
        name='', default='Equal',
        update=remove_extra_inputs)
    min_inputs = 2
    property1: HaxeFloatProperty('property1', name='Tolerance', description='Precision for float compare', default=0.0001)

    def __init__(self):
        super(CompareNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Value')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmBoolSocket', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

        if self.property0 == 'Almost Equal':
            layout.prop(self, 'property1')

        if any(p == self.property0 for p in ['Or', 'And']):
            row = layout.row(align=True)
            op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
            op.node_index = str(id(self))
            op.socket_type = 'ArmDynamicSocket'
            op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op2.node_index = str(id(self))
