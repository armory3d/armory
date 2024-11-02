from arm.logicnode.arm_nodes import *

class OneShotActionMultiNode(ArmLogicTreeNode):
    """Introduce one loop of animation in the current tree using the selected action."""
    bl_idname = 'LNOneShotActionMultiNode'
    bl_label = 'One Shot Action Multi'
    bl_width_default = 250
    arm_version = 1
    min_inputs = 10

    def __init__(self):
        super(OneShotActionMultiNode, self).__init__()
        array_nodes[self.get_id_str()] = self

    property0: HaxeStringProperty('property0', name = 'Action ID', default = '')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmIntSocket', 'Index', default_value = 0)
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmBoolSocket', 'Restart', default_value = True)
        self.add_input('ArmFloatSocket', 'Blend In Time', default_value = 1.0)
        self.add_input('ArmFloatSocket', 'Blend Out Time', default_value = 1.0)
        self.add_input('ArmIntSocket', 'Bone Group', default_value = -1)
        self.add_input('ArmNodeSocketAnimTree', 'Main Action')
        self.add_input('ArmNodeSocketAnimAction', 'Action 0')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('ArmNodeSocketAnimTree', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = self.get_id_str()
        op.socket_type = 'ArmNodeSocketAnimAction'
        op.name_format = 'Action {0}'
        op.index_name_offset = -9
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = self.get_id_str()
        if len(self.inputs) == self.min_inputs:
            column.enabled = False