from arm.logicnode.arm_nodes import *
import re

class MathTermNode(ArmLogicTreeNode):
    """Formula for symbolic Math"""
    bl_idname = 'LNMathTermNode'
    bl_label = 'Math Term'
    arm_version = 0

    num_params: IntProperty(default=2, min=0)

    property0: HaxeBoolProperty('property0', name='Resolve params', description='Resolve input param values/subterms for output term/transformations', default=False)

    def __init__(self, *args, **kwargs):
        super(MathTermNode, self).__init__(*args, **kwargs)
        self.register_id()


    def arm_init(self, context):

        # OUTPUTS:
        self.add_output('ArmDynamicSocket', 'Math Term')
        self.add_output('ArmDynamicSocket', 'Simplifyed')
        self.add_output('ArmDynamicSocket', 'Derivate')
        self.add_output('ArmFloatSocket', 'Result')
        self.add_output('ArmStringSocket', 'Error')
        self.add_output('ArmIntSocket', 'ErrorPos')

        # INPUTS:

        # HOW to setup a Tooltip here and how to put it above the param-add/remove-buttons into layout ?
        self.add_input('ArmStringSocket', 'Math Term', default_value='a+b')

        # two default parameters at start
        self.add_input('ArmStringSocket', 'Param 0', default_value='a')
        self.add_input('ArmDynamicSocket', 'Value / Term 0')

        self.add_input('ArmStringSocket', 'Param 1', default_value='b')
        self.add_input('ArmDynamicSocket', 'Value / Term 1')

    def add_sockets(self):
        self.add_input('ArmStringSocket', 'Name ' + str(self.num_params))
        #self.add_input('ArmFloatSocket', 'Value ' + str(self.num_params))
        self.add_input('ArmDynamicSocket', 'Value / Term ' + str(self.num_params))
        self.num_params += 1

    def remove_sockets(self):
        if self.num_params > 0:
            self.inputs.remove(self.inputs.values()[-1])
            self.inputs.remove(self.inputs.values()[-1])
            self.num_params -= 1

    def draw_buttons(self, context, layout):
        # Bind values to params Property
        layout.prop(self, 'property0')

        # Button ADD parameter
        row = layout.row(align=True)
        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='Add Param', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.callback_name = 'add_sockets'

        # Button REMOVE parameter
        column = row.column(align=True)
        op = column.operator('arm.node_call_func', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        op.callback_name = 'remove_sockets'
        if self.num_params == 0:
            column.enabled = False
